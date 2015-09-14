/*

2015-09-13

n is number of events

n' is number of adds/removes

n'' is number of solve events

n_max is window size

W is capacity

algorithm takes O(n * W) time

inspired by chao xu and lei huang

involves dynamic programming

for on-line knapsack problem

uses two stacks and decomposition

comparable with naive dp approach, 
  which has running time:
  O(n'' * n_max * W)

comparable with branch-and-bound approach, 
  which has running time:
  O(n'' * (log(n_max) + n_max))

*/

import java.util.ArrayList;
import java.util.PriorityQueue;
import java.util.Comparator;
import java.lang.Exception;
import java.lang.Integer;
import java.lang.Math;
import java.lang.StringBuilder;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.InputStream;
import java.lang.String;
abstract class Event {
	int time;
	public Event(int time) {
		this.time = time;
	}
	public int getTime() {
		return this.time;
	}
	public boolean isSolveEvent() {
		return false;
	}
	public void handle(ArrayList<SackItem> sack_item_collection, 
			SackItemTable left_table, SackItemTable right_table, 
			WeightContainer weight_container, 
			ProblemChangedContainer changed_container) {
		return;
	}
}
class EventPriorityQueue {
	PriorityQueue<Tuple<Event, Integer>> pq;
	public EventPriorityQueue() {
		EventPriorityTupleComparator comparator = 
				new EventPriorityTupleComparator();
		this.pq = new PriorityQueue<Tuple<Event, Integer>>(10, comparator);
	}
	public void push(Event item, int priority) {
		Tuple<Event, Integer> next_item = 
				new Tuple<Event, Integer>(item, priority);
		(this.pq).add(next_item);
	}
	public Event pop() {
		Tuple<Event, Integer> item = (this.pq).poll();
		Event e = item.x;
		return e;
	}
	public boolean isEmpty() {
		return (this.pq).size() == 0;
	}
	public Event peek() {
		Tuple<Event, Integer> item = (this.pq).peek();
		Event e = item.x;
		return e;
	}
}
class EventPriorityTupleComparator implements Comparator<Tuple<Event, Integer>> {
	public int compare(Tuple<Event, Integer> a, Tuple<Event, Integer> b) {
		int time_a = a.y;
		int time_b = b.y;
		if (time_a < time_b) {
			return -1;
		} else if (time_a > time_b) {
			return 1;
		} else {
			return 0;
		}
	}
}
class FeedItem {
	int profit, weight, id_value;
	public FeedItem(int profit, int weight, int id_value) {
		this.profit = profit;
		this.weight = weight;
		this.id_value = id_value;
	}
	public int getProfit() {
		return this.profit;
	}
	public int getWeight() {
		return this.weight;
	}
	public int getIDValue() {
		return this.id_value;
	}
	static public SackItem toSackItem(FeedItem feed_item) {
		SackItem sack_item = new SackItem(feed_item.getProfit(), 
				feed_item.getWeight(), feed_item.getIDValue());
		return sack_item;
	}
}
abstract class ItemEvent extends Event {
	FeedItem item;
	public ItemEvent(int time, FeedItem item) {
		super(time);
		this.item = item;
	}
	public FeedItem getItem() {
		return this.item;
	}
}
class ItemExpireEvent extends ItemEvent {
	public ItemExpireEvent(int time, FeedItem item) {
		super(time, item);
	}
	public String toString() {
		FeedItem item = this.getItem();
		int id_value = item.getIDValue();
		ArrayList<String> component_str_list = new ArrayList<String>();
		component_str_list.add("item expire event:");
		component_str_list.add(String.valueOf(id_value));
		String result_str = Util.join(component_str_list, " ");
		return result_str;
	}
	public void handle(ArrayList<SackItem> sack_item_collection, 
			SackItemTable left_table, SackItemTable right_table, 
			WeightContainer weight_container, 
			ProblemChangedContainer changed_container) {
		FeedItem item = this.getItem();
		int id_value = item.getIDValue();
		sack_item_collection.remove(0);
		left_table.popRow(right_table);
		int weight = item.getWeight();
		weight_container.setWeight(weight_container.getWeight() - weight);
		changed_container.setChanged(true);
	}
}
class ItemIntroduceEvent extends ItemEvent {
	public ItemIntroduceEvent(int time, FeedItem item) {
		super(time, item);
	}
	public String toString() {
		FeedItem item = this.getItem();
		int id_value = item.getIDValue();
		ArrayList<String> component_str_list = new ArrayList<String>();
		component_str_list.add("item introduce event:");
		component_str_list.add(String.valueOf(id_value));
		String result_str = Util.join(component_str_list, " ");
		return result_str;
	}
	public void handle(ArrayList<SackItem> sack_item_collection, 
			SackItemTable left_table, SackItemTable right_table, 
			WeightContainer weight_container, 
			ProblemChangedContainer changed_container) {
		FeedItem item = this.getItem();
		int id_value = item.getIDValue();
		SackItem sack_item = FeedItem.toSackItem(item);
		sack_item_collection.add(sack_item);
		right_table.pushRow(sack_item);
		int weight = item.getWeight();
		weight_container.setWeight(weight_container.getWeight() + weight);
		changed_container.setChanged(true);
	}
}
class ItemTimeSpanningEvent extends ItemEvent {
	public ItemTimeSpanningEvent(int time, FeedItem item) {
		super(time, item);
	}
	public String toString() {
		FeedItem item = this.getItem();
		int time = this.getTime();
		int profit = item.getProfit();
		int weight = item.getWeight();
		int id_value = item.getIDValue();
		ArrayList<String> components = new ArrayList<String>();
		components.add("item time-spanning event:");
		components.add(String.valueOf(time));
		components.add(String.valueOf(profit));
		components.add(String.valueOf(weight));
		components.add(String.valueOf(id_value));
		String result = Util.join(components,  " ");
		return result;
	}
}
class LazyIDCollectionTable {
	int C;
	ArrayList<ArrayList<ArrayList<Integer>>> rows;
	boolean[][] is_cached_rows;
	int num_active_rows;
	public LazyIDCollectionTable(int C, int n_max) {
		this.C = C;
		ArrayList<ArrayList<ArrayList<Integer>>> rows = 
				new ArrayList<ArrayList<ArrayList<Integer>>>();
		// for (int i : Util.range(n_max + 1)) {
		int i_end = n_max + 1;
		for (int i = 0; i < i_end; i++) {
			ArrayList<ArrayList<Integer>> row = Util.fill(null, C + 1);
			rows.add(row);
		}
		this.rows = rows;
		boolean[][] is_cached_rows = 
				new boolean[n_max + 1][C + 1];
		/*
		// for (int i : Util.range(n_max + 1)) {
		// i_end = n_max + 1;
		for (int i = 0; i < i_end; i++) {
			ArrayList<Boolean> is_cached_row = Util.fill(false, C + 1);
			is_cached_rows.add(is_cached_row);
		}
		 */
		this.is_cached_rows = is_cached_rows;
		ArrayList<ArrayList<Integer>> row = Util.fill(null, C + 1);
		rows.add(row);
		/*
		ArrayList<Boolean> is_cached_row = Util.fill(false, C + 1);
		is_cached_rows.add(is_cached_row);
		 */
		for (int i = 0; i < C + 1; i++) {
			is_cached_rows[0][i] = false;
		}
		this.num_active_rows = 0;
	}
	public boolean[][] _getIsCachedRows() {
		return this.is_cached_rows;
	}
	public ArrayList<Integer> getCell(int i, int j, 
			SackItemTable sack_item_table, boolean from_left_table) {
		int num_active_rows = this._getNumActiveRows();
		boolean is_cached = false;
		if (i <= num_active_rows - 1 - 1) {
			is_cached = (this.is_cached_rows)[i][j];
		}
		ArrayList<Integer> value;
		if (is_cached == false) {
			value = Util.reconstituteItemCollectionFromCell(i, j, 
					sack_item_table, from_left_table);
			(this.rows).get(i).set(j, value);
			(this.is_cached_rows)[i][j] = true;
			return value;
		} else {
			value = (this.rows).get(i).get(j);
			return value;
		}
	}
	public int _getNumActiveRows() {
		return this.num_active_rows;
	}
	public void _setNumActiveRows(int n) {
		this.num_active_rows = n;
	}
	public void pushRow(SackItem sack_item) {
		ArrayList<ArrayList<Integer>> row = Util.fill(null, C + 1);
		rows.add(row);
		int num_active_rows = this._getNumActiveRows();
		for (int i = 0; i < C + 1; i++) {
			int row_index = num_active_rows + 1;
			is_cached_rows[row_index][i] = false;
		}
	}
	public void popRow() {
		rows.remove(rows.size() - 1);
		// is_cached_rows.remove(is_cached_rows.size() - 1);
	}
}
class ProblemChangedContainer {
	boolean changed;
	String prev_sol_str;
	public ProblemChangedContainer(boolean changed, String prev_sol_str) {
		this.changed = changed;
		this.prev_sol_str = prev_sol_str;
	}
	public boolean getChanged() {
		return this.changed;
	}
	public void setChanged(boolean changed) {
		this.changed = changed;
	}
	public String getPrevSolutionString() {
		return this.prev_sol_str;
	}
	public void setPrevSolutionString(String prev_sol_str) {
		this.prev_sol_str = prev_sol_str;
	}
}
class SackItem {
	int profit, weight, identifier_value;
	public SackItem(int profit, int weight, int identifier_value) {
		this.profit = profit;
		this.weight = weight;
		this.identifier_value = identifier_value;
	}
	public int getProfit() {
		return this.profit;
	}
	public int getWeight() {
		return this.weight;
	}
	public int getIdentifierValue() {
		return this.identifier_value;
	}
	public String toString() {
		int profit = this.getProfit();
		int weight = this.getWeight();
		String result = "(" + String.valueOf(profit) + 
				", " + String.valueOf(weight) + ")";
		return result;
	}
}
class SackItemTable {
	int C, num_sack_items;
	int[][] profit_rows;
	Util.BackPointer[][] back_pointer_rows;
	int[][] size_rows;
	LazyIDCollectionTable id_collection_table;
	int num_active_rows;
	ArrayList<SackItem> sack_items;
	boolean is_left_table;
	public SackItemTable(int C, int n_max, boolean is_left_table, int num_sack_items) {
		this.C = C;
		this.num_sack_items = num_sack_items;
		int[][] profit_rows = 
				new int[n_max + 1][C + 1];
		// for (int i : Util.range(n_max + 1)) {
		/*
		int i_end = n_max + 1;
		for (int i = 0; i < i_end; i++) {
			ArrayList<Integer> profit_row = Util.fill(0, C + 1);
			profit_rows.add(profit_row);
		}
		 */
		this.profit_rows = profit_rows;
		Util.BackPointer[][] back_pointer_rows = 
				new Util.BackPointer[n_max + 1][C + 1];
		// for (int i : Util.range(n_max + 1)) {
		/*
		i_end = n_max + 1;
		for (int i = 0; i < i_end; i++) {
			ArrayList<Util.BackPointer> back_pointer_row = 
					Util.fill(Util.BackPointer.BASE, C + 1);
			back_pointer_rows.add(back_pointer_row);
		}
		 */
		this.back_pointer_rows = back_pointer_rows;
		int[][] size_rows = 
				new int[n_max + 1][C + 1];
		// for (int i : Util.range(n_max + 1)) {
		/*
		i_end = n_max + 1;
		for (int i = 0; i < i_end; i++) {
			ArrayList<Integer> size_row = Util.fill(0, C + 1);
			size_rows.add(size_row);
		}
		 */
		this.size_rows = size_rows;
		this.id_collection_table = new LazyIDCollectionTable(C, n_max);
		for (int i = 0; i < C + 1; i++) {
			profit_rows[0][i] = 0;
			back_pointer_rows[0][i] = Util.BackPointer.BASE;
			size_rows[0][i] = 0;
		}
		id_collection_table.pushRow(null);
		this.num_active_rows = 0;
		this.sack_items = new ArrayList<SackItem>();
		this.is_left_table = is_left_table;
	}
	public int[][] _getProfitRows() {
		return this.profit_rows;
	}
	public int[][] _getSizeRows() {
		return this.size_rows;
	}
	public LazyIDCollectionTable _getIDCollectionTable() {
		return this.id_collection_table;
	}
	public Util.BackPointer[][] _getBackPointerRows() {
		return this.back_pointer_rows;
	}
	public ArrayList<SackItem> _getSackItems() {
		return this.sack_items;
	}
	public boolean _getIsLeftTable() {
		return this.is_left_table;
	}
	public int getCapacity() {
		return this.C;
	}
	public int getNumSackItems() {
		return this.num_sack_items;
	}
	public boolean haveZeroSackItems() {
		return this.getNumSackItems() == 0;
	}
	public int _getNumActiveRows() {
		return this.num_active_rows;
	}
	public void pushRow(SackItem sack_item) {
		int num_active_rows = this._getNumActiveRows();
		for (int i = 0; i < C + 1; i++) {
			int row_index = num_active_rows + 1;
			profit_rows[row_index][i] = 0;
			back_pointer_rows[row_index][i] = Util.BackPointer.BASE;
			size_rows[row_index][i] = 0;
		}
		id_collection_table.pushRow(sack_item);
		int[][] profit_rows = this.profit_rows;
		Util.BackPointer[][] back_pointer_rows = this.back_pointer_rows;
		int[][] size_rows = this.size_rows;
		int profit = sack_item.profit;
		int weight = sack_item.weight;
		int identifier_value = sack_item.identifier_value;
		int j = this._getNumActiveRows() + 1;
		// LazyIDCollectionTable id_collection_table = this._getIDCollectionTable();
		LazyIDCollectionTable id_collection_table = this.id_collection_table;
		id_collection_table._setNumActiveRows(id_collection_table._getNumActiveRows() + 1);
		int[] prev_row = profit_rows[j - 1];
		int[] curr_row = profit_rows[j];
		Util.BackPointer[] curr_bp_row = back_pointer_rows[j];
		int[] prev_size_row = size_rows[j - 1];
		int[] curr_size_row = size_rows[j];
		// for (int w : Util.range(this.getCapacity() + 1)) {
		int w_end = this.getCapacity() + 1;
		for (int w = 0; w < w_end; w++) {
			if (weight > w) {
				curr_row[w] = prev_row[w];
				curr_bp_row[w] = Util.BackPointer.WITHOUT;
				curr_size_row[w] = prev_size_row[w];
			} else {
				int prev_profit = prev_row[w - weight];
				int with_profit = prev_profit + profit;
				int without_profit = prev_row[w];
				int with_size = prev_size_row[w - weight] + 1;
				int without_size = prev_size_row[w];
				boolean prefer_with = Util.compareScore(with_profit, 
						without_profit, with_size, without_size, 
						this, j - 1, w - weight, j - 1, w, 
						this.is_left_table, identifier_value) == 1;
				/*
				curr_size_row.set(w, prefer_with ? prev_size_row.get(w - weight) + 1 
						: prev_size_row.get(w));
				 */
				curr_size_row[w] = prefer_with ? with_size : without_size;
				curr_bp_row[w] = prefer_with ? Util.BackPointer.WITH 
						: Util.BackPointer.WITHOUT;
				int next_profit = prefer_with ? with_profit : without_profit;
				curr_row[w] = next_profit;
			}
		}
		this.num_sack_items += 1;
		(this.sack_items).add(sack_item);
		this.num_active_rows += 1;
	}
	public Tuple<int[], SackItem> _popRowHelper(SackItemTable right_table) {
		id_collection_table.popRow();
		int[][] profit_rows = this.profit_rows;
		int num_active_rows = this._getNumActiveRows();
		int[] profit_row = profit_rows[num_active_rows - 1];
		this.num_sack_items -= 1;
		ArrayList<SackItem> sack_items = this.sack_items;
		int index = sack_items.size() - 1;
		SackItem sack_item = sack_items.get(index);
		sack_items.remove(index);
		this.num_active_rows -= 1;
		LazyIDCollectionTable id_collection_table = this._getIDCollectionTable();
		id_collection_table._setNumActiveRows(id_collection_table._getNumActiveRows() - 1);
		Tuple<int[], SackItem> result = 
				new Tuple<int[], SackItem>(profit_row, sack_item);
		return result;
	}
	public Tuple<int[], SackItem> popRow(SackItemTable right_table) {
		if (this.haveZeroSackItems() == true) {
			if (right_table.haveZeroSackItems() == true) {
				// throw new Exception();
				return null;
			} else {
				while (right_table.haveZeroSackItems() == false) {
					Tuple<int[], SackItem> result = 
							right_table._popRowHelper(right_table);
					int[] row = result.x;
					SackItem sack_item = result.y;
					this.pushRow(sack_item);
				}
			}
		}
		Tuple<int[], SackItem> result = 
				this._popRowHelper(right_table);
		return result;
	}
	static public Tuple<Integer, ArrayList<Integer>> combine(SackItemTable left_table, 
			SackItemTable right_table) {
		int capacity = left_table.getCapacity();
		int num_active_rows1 = left_table._getNumActiveRows();
		int num_active_rows2 = right_table._getNumActiveRows();
		int[][] profit_rows1 = left_table._getProfitRows();
		int[][] profit_rows2 = right_table._getProfitRows();
		int[] curr_profit_row1 = profit_rows1[num_active_rows1];
		int[] curr_profit_row2 = profit_rows2[num_active_rows2];
		int min_int = Integer.MIN_VALUE;
		int best_profit = min_int;
		// for (int curr_capacity : Util.range(capacity + 1)) {
		int i_end = capacity + 1;
		for (int curr_capacity = 0; curr_capacity < i_end; curr_capacity++) {
			int residual_capacity = capacity - curr_capacity;
			int curr_profit = 
					curr_profit_row1[curr_capacity] + 
					curr_profit_row2[residual_capacity];
			best_profit = Math.max(curr_profit, best_profit);
		}
		ArrayList<Tuple<ArrayList<Integer>, ArrayList<Integer>>> left_right_solution_pairs = 
				new ArrayList<Tuple<ArrayList<Integer>, ArrayList<Integer>>>();
		// for (int curr_capacity : Util.range(capacity + 1)) {
		i_end = capacity + 1;
		for (int curr_capacity = 0; curr_capacity < i_end; curr_capacity++) {
			int residual_capacity = capacity - curr_capacity;
			int left_profit = curr_profit_row1[curr_capacity];
			int right_profit = curr_profit_row2[residual_capacity];
			int curr_profit = left_profit + right_profit;
			if (curr_profit == best_profit) {
				ArrayList<Integer> left_solution = 
						Util.reconstituteItemCollectionFromCell(num_active_rows1, curr_capacity, left_table, true);
				ArrayList<Integer> right_solution = 
						Util.reconstituteItemCollectionFromCell(num_active_rows2, residual_capacity, right_table, false);
				Tuple<ArrayList<Integer>, ArrayList<Integer>> left_right_solution_pair = 
						new Tuple<ArrayList<Integer>, ArrayList<Integer>>(left_solution, right_solution);
				left_right_solution_pairs.add(left_right_solution_pair);
			}
		}
		F1 f = new F1(best_profit);
		Tuple<ArrayList<Integer>, ArrayList<Integer>> chosen_left_right_solution_pair = 
				Util.reduceLeft(f, left_right_solution_pairs);
		ArrayList<Integer> chosen_left_solution = chosen_left_right_solution_pair.x;
		ArrayList<Integer> chosen_right_solution = chosen_left_right_solution_pair.y;
		ArrayList<Integer> combined_solution = Util.concatenate(chosen_left_solution, chosen_right_solution);
		Tuple<Integer, ArrayList<Integer>> result = 
				new Tuple<Integer, ArrayList<Integer>>(best_profit, combined_solution);
		return result;
	}
	public String toString() {
		int num_active_rows = this._getNumActiveRows();
		int[][] profit_rows = this._getProfitRows();
		ArrayList<ArrayList<Integer>> next_profit_rows = 
				new ArrayList<ArrayList<Integer>>();
		for (int[] profit_row : profit_rows) {
			ArrayList<Integer> next_profit_row = new ArrayList<Integer>();
			for (int profit_value : profit_row) {
				next_profit_row.add(profit_value);
			}
			next_profit_rows.add(next_profit_row);
		}
		F3 f = new F3();
		ArrayList<String> profit_row_str_list = Util.map(f, next_profit_rows);
		String result = Util.join(profit_row_str_list, "\n");
		return result;
	}
}
class F1 implements BinaryFunc<Tuple<ArrayList<Integer>, ArrayList<Integer>>, 
Tuple<ArrayList<Integer>, ArrayList<Integer>>> {
	int profit;
	public F1(int profit) {
		this.profit = profit;
	}
	public Tuple<ArrayList<Integer>, ArrayList<Integer>> 
	call(Tuple<ArrayList<Integer>, ArrayList<Integer>> a, 
			Tuple<ArrayList<Integer>, ArrayList<Integer>> b) {
		int profit = this.profit;
		ArrayList<Integer> sorted_id_list1 = Util.concatenate(a.x, a.y);
		ArrayList<Integer> sorted_id_list2 = Util.concatenate(b.x, b.y);
		int result = Util.compareScore2(profit, profit, 
				sorted_id_list1, sorted_id_list2);
		if (result == -1) {
			return b;
		} else {
			return a;
		}
	}
}
class F2 implements UnaryFunc<Integer, String> {
	public F2() {
	}
	public String call(Integer a) {
		return a.toString();
	}
}
class F3 implements UnaryFunc<ArrayList<Integer>, String> {
	F2 f;
	public F3() {
		this.f = new F2(); 
	}
	public String call(ArrayList<Integer> a) {
		ArrayList<String> result = Util.map(this.f, a);
		String next_result = Util.join(result, " ");
		return next_result;
	}
}
class SackProblem {
	ArrayList<SackItem> sack_items;
	int capacity;
	public SackProblem(ArrayList<SackItem> sack_items, int capacity) {
		this.sack_items = sack_items;
		this.capacity = capacity;
	}
	public ArrayList<SackItem> getSackItems() {
		return this.sack_items;
	}
	public int getCapacity() {
		return this.capacity;
	}
	public void setCapacity(int capacity) {
		this.capacity = capacity;
	}
	public String solve(SackItemTable left_table, SackItemTable right_table) {
		Tuple<Integer, ArrayList<Integer>> result = 
				SackItemTable.combine(left_table, right_table);
		int profit = result.x;
		ArrayList<Integer> sorted_id_values = result.y;
		int size = sorted_id_values.size();
		ArrayList<Integer> components = new ArrayList<Integer>();
		components.add(profit);
		components.add(size);
		components = Util.concatenate(components, sorted_id_values);
		F2 f2 = new F2();
		ArrayList<String> component_str_list = Util.map(f2, components);
		String result_str = Util.join(component_str_list, " ");
		return result_str;
	}
}
public class Solution {
	public static void main(String args[]) throws Exception {
		WeightContainer weight_container = new WeightContainer(0);
		ProblemChangedContainer changed_container = new ProblemChangedContainer(true, null);
		// InputStream in = new FileInputStream("/home/brianl/workspace/feed_optimizer_java/src/feed_optimizer_java/tests/official/input01.txt");
		InputStream in = System.in;
		InputStreamReader stream_reader = new InputStreamReader(in);
		BufferedReader br = new BufferedReader(stream_reader);
		String line = br.readLine();
		line = line.trim();
		String[] curr_args = line.split(" ");
		int n_instr = Integer.valueOf(curr_args[0]);
		int n_max = Integer.valueOf(curr_args[1]);
		int W = Integer.valueOf(curr_args[2]);
		int curr_id_value = 1;
		ArrayList<ItemTimeSpanningEvent> item_time_spanning_events = 
				new ArrayList<ItemTimeSpanningEvent>();
		ArrayList<SolveEvent> solve_events = 
				new ArrayList<SolveEvent>();
		// for (int i : Util.range(n_instr)) {
		int i_end = n_instr;
		for (int i = 0; i < i_end; i++) {
			line = br.readLine();
			line = line.trim();
			curr_args = line.split(" ");
			String event_type = curr_args[0];
			if (event_type.equals("S")) {
				int time = Integer.valueOf(curr_args[1]);
				int profit = Integer.valueOf(curr_args[2]);
				int weight = Integer.valueOf(curr_args[3]);
				FeedItem item = new FeedItem(profit, weight, curr_id_value);
				ItemTimeSpanningEvent item_time_spanning_event = 
						new ItemTimeSpanningEvent(time, item);
				item_time_spanning_events.add(item_time_spanning_event);
				curr_id_value = curr_id_value + 1;
			} else if (event_type.equals("R")) {
				int time = Integer.valueOf(curr_args[1]);
				SolveEvent solve_event = new SolveEvent(time, W);
				solve_events.add(solve_event);
			} else {
				throw new Exception("event of unknown type encountered");
			}
		}
		ArrayList<FeedItem> items = new ArrayList<FeedItem>();
		EventPriorityQueue non_expire_event_priority_queue = new EventPriorityQueue();
		EventPriorityQueue expire_event_priority_queue = new EventPriorityQueue();
		for (ItemTimeSpanningEvent event : item_time_spanning_events) {
			int time = event.getTime();
			FeedItem item = event.getItem();
			int profit = item.getProfit();
			int weight = item.getWeight();
			int id_value = item.getIDValue();
			int introduce_time = time;
			int expire_time = time + n_max + 1;
			ItemIntroduceEvent item_introduce_event = new ItemIntroduceEvent(introduce_time, item);
			ItemExpireEvent item_expire_event = new ItemExpireEvent(expire_time, item);
			non_expire_event_priority_queue.push(item_introduce_event, introduce_time);
			expire_event_priority_queue.push(item_expire_event, expire_time);
			items.add(item);
		}
		for (SolveEvent event : solve_events) {
			int time = event.getTime();
			non_expire_event_priority_queue.push(event, time);
		}
		ArrayList<SackItem> curr_sack_item_collection = new ArrayList<SackItem>();
		/*
		int left_table_size = n_max;
		int right_table_size = n_max;
		 */
		SackItemTable left_table = new SackItemTable(W, n_max, true, 0);
		SackItemTable right_table = new SackItemTable(W, n_max, false, 0);
		int remaining_solve_events = solve_events.size();
		while(expire_event_priority_queue.isEmpty() == false || 
				non_expire_event_priority_queue.isEmpty() == false) {
			if (remaining_solve_events == 0) {
				break;
			}
			boolean expire_event_exists = expire_event_priority_queue.isEmpty() == false;
			boolean non_expire_event_exists = non_expire_event_priority_queue.isEmpty() == false;
			boolean favor_expire_event;
			if (expire_event_exists == false && non_expire_event_exists == true) {
				favor_expire_event = false;
			} else if (expire_event_exists == true && non_expire_event_exists == false) {
				favor_expire_event = true;
			} else if (expire_event_exists == true && non_expire_event_exists == true) {
				ItemExpireEvent expire_event = (ItemExpireEvent) expire_event_priority_queue.peek();
				Event non_expire_event = non_expire_event_priority_queue.peek();
				int expire_event_time = expire_event.getTime();
				int non_expire_event_time = non_expire_event.getTime();
				if (expire_event_time <= non_expire_event_time) {
					favor_expire_event = true;
				} else {
					favor_expire_event = false;
				}
				Event event;
				if (favor_expire_event == true) {
					event = expire_event_priority_queue.pop();
				} else {
					event = non_expire_event_priority_queue.pop();
				}
				event.handle(curr_sack_item_collection, left_table, right_table, 
						weight_container, changed_container);
				if (event.isSolveEvent() == true) {
					remaining_solve_events -= 1;
				}
			}
		}
	}
}
class SolveEvent extends Event {
	int sack_capacity;
	public SolveEvent(int time, int sack_capacity) {
		super(time);
		this.sack_capacity = sack_capacity;
	}
	public int _getSackCapacity() {
		return this.sack_capacity;
	}
	public String toString() {
		int time = this.getTime();
		ArrayList<String> components = new ArrayList<String>();
		components.add("solve event:");
		components.add(String.valueOf(time));
		String result = Util.join(components, " ");
		return result;
	}
	public void handle(ArrayList<SackItem> sack_item_collection, 
			SackItemTable left_table, SackItemTable right_table, 
			WeightContainer weight_container, 
			ProblemChangedContainer changed_container) {
		int capacity = this.sack_capacity;
		int curr_total_weight = weight_container.weight;
		boolean changed_status = changed_container.getChanged();
		if (changed_status == false) {
			String result_str = changed_container.getPrevSolutionString();
			System.out.println(result_str);
			return;
		}
		if (curr_total_weight <= capacity) {
			ArrayList<SackItem> sack_items = sack_item_collection;
			F5 f5 = new F5();
			ArrayList<Integer> id_values = Util.map(f5, sack_items);
			F6 f6 = new F6();
			ArrayList<Integer> profit_values = Util.map(f6, sack_items);
			int profit = Util.sum(profit_values);
			int size = id_values.size();
			ArrayList<Integer> components = new ArrayList<Integer>();
			components.add(profit);
			components.add(size);
			components = Util.concatenate(components, id_values);
			F2 f2 = new F2();
			ArrayList<String> component_str_list = Util.map(f2, components);
			String result_str = Util.join(component_str_list, " ");
			System.out.println(result_str);
			changed_container.setPrevSolutionString(result_str);
			changed_container.setChanged(false);
		} else {
			ArrayList<SackItem> sack_items = sack_item_collection;
			SackProblem sack_problem = new SackProblem(sack_items, this._getSackCapacity());
			String result_str = sack_problem.solve(left_table, right_table);
			System.out.println(result_str);
			changed_container.setPrevSolutionString(result_str);
			changed_container.setChanged(false);
		}
	}
	public boolean isSolveEvent() {
		return true;
	}
}
class Tuple<X, Y> {
	public final X x;
	public final Y y;
	public Tuple(X x, Y y) {
		this.x = x;
		this.y = y;
	}
}
class Util {
	public enum BackPointer {
		WITH, WITHOUT, BASE
	}
	// size1 is assumed to be for "with" case
	static public int compareScore(int profit1, int profit2, int size1, int size2, 
			SackItemTable sack_item_table, int i1, int j1, int i2, int j2, 
			boolean from_left_table, int identifier_value) {
		if (profit1 < profit2) {
			return -1;
		} else if (profit1 > profit2) {
			return 1;
		} else {
			if (size1 > size2) {
				return -1;
			} else if (size1 < size2) {
				return 1;
			} else {
				LazyIDCollectionTable id_collection_table = 
						sack_item_table.id_collection_table;
				ArrayList<Integer> sorted_id_list1 = 
						id_collection_table.getCell(i1, j1, sack_item_table, from_left_table);
				// ArrayList<Integer> next_sorted_id_list1 = (ArrayList<Integer>) sorted_id_list1.clone();
				ArrayList<Integer> next_sorted_id_list1 = new ArrayList<Integer>(sorted_id_list1.size() + 1);
				if (from_left_table == true) {
					// sizes are equal
					for (int i = 0; i < size1 - 1; i++) {
						Integer value = sorted_id_list1.get(i);
						next_sorted_id_list1.add(value);
					}
					next_sorted_id_list1.add(identifier_value);
				} else {
					next_sorted_id_list1.add(identifier_value);
					// sizes are equal
					for (int i = 0; i < size1 - 1; i++) {
						Integer value = sorted_id_list1.get(i);
						next_sorted_id_list1.add(value);
					}
					// next_sorted_id_list1.add(0, identifier_value);
				}
				ArrayList<Integer> sorted_id_list2 = 
						id_collection_table.getCell(i2, j2, sack_item_table, from_left_table);
				// for (int i : Util.range(Math.min(sorted_id_list1.size(), sorted_id_list2.size()))) {
				// int i_end = Math.min(sorted_id_list1.size(),  sorted_id_list2.size());
				// sizes are equal
				int i_end = size1;
				for (int i = 0; i < i_end; i++) {
					int id1 = next_sorted_id_list1.get(i);
					int id2 = sorted_id_list2.get(i);
					if (id1 > id2) {
						return -1;
					} else if (id1 < id2) {
						return 1;
					}
				}
				return 0;
			}
		}
	}
	static public int compareScore2(int profit1, int profit2, 
			ArrayList<Integer> sorted_id_list1, ArrayList<Integer> sorted_id_list2) {
		if (profit1 < profit2) {
			return -1;
		} else if (profit1 > profit2) {
			return 1;
		} else {
			int size1 = sorted_id_list1.size();
			int size2 = sorted_id_list2.size();
			if (size1 > size2) {
				return -1;
			} else if (size1 < size2) {
				return 1;
			} else {
				int i_end = sorted_id_list1.size();
				// for (int i : Util.range(sorted_id_list1.size())) {
				for (int i = 0; i < i_end; i++) {
					int id1 = sorted_id_list1.get(i);
					int id2 = sorted_id_list2.get(i);
					if (id1 > id2) {
						return -1;
					} else if (id1 < id2) {
						return 1;
					}
				}
				return 0;
			}
		}
	}
	static public ArrayList<Integer> reconstituteItemCollectionFromCell(int i, int j, 
			SackItemTable table, boolean from_left_table) {
		BackPointer[][] back_pointer_rows = 
				table.back_pointer_rows;
		ArrayList<SackItem> sack_items = table.sack_items;
		ArrayList<Integer> id_values = new ArrayList<Integer>();
		BackPointer curr_bp_value = back_pointer_rows[i][j];
		int curr_i = i;
		int curr_j = j;
		BackPointer used;
		while (curr_bp_value != BackPointer.BASE) {
			used = curr_bp_value;
			if (used == BackPointer.WITH) {
				SackItem curr_sack_item = sack_items.get(curr_i - 1);
				int id_value = curr_sack_item.identifier_value;
				id_values.add(id_value);
				int weight = curr_sack_item.weight;
				curr_i = curr_i - 1;
				int next_weight = Math.max(0, curr_j - weight);
				// curr_j = ((curr_j - weight) < 0) ? 0 : (curr_j - weight);
				curr_j = next_weight;
			} else {
				curr_i = curr_i - 1;
				// curr_j = curr_j;
			}
			curr_bp_value = back_pointer_rows[curr_i][curr_j];
		}
		ArrayList<Integer> result;
		if (from_left_table == true) {
			// result = (ArrayList<Integer>) id_values.clone();
			result = id_values;
		} else {
			// result = (ArrayList<Integer>) id_values.clone();
			result = id_values;
			Util.reverse(result);
		}
		return result;
	}
	static public ArrayList<Integer> range(int x) {
		ArrayList<Integer> result = new ArrayList<Integer>(x);
		for (int i = 0; i < x; i++) {
			result.add(i);
		}
		return result;
	}
	static public <E> ArrayList<E> reverse(ArrayList<E> list) {
		if (list.size() == 0) {
			return list;
		} else {
			E value = list.remove(0);
			Util.reverse(list);
			list.add(value);
			return list;
		}
	}
	static public <E> ArrayList<E> fill(E item, int n) {
		ArrayList<E> list = new ArrayList<E>(n);
		for (int i = 0; i < n; i++) {
			list.add(item);
		}
		return list;
	}
	static public <T> T foldLeft(BinaryFunc<T, T> f, ArrayList<T> collection, T init) {
		for (T item : collection) {
			init = f.call(init, item);
		}
		return init;
	}
	static public <T> T reduceLeft(BinaryFunc<T, T> f, ArrayList<T> collection) {
		int size = collection.size();
		if (size == 0) {
			/*
			try {
				// throw new Exception();
			} catch (Exception e) {
				System.out.println(e);
			}
			 */
			return null;
		} else {
			T init = collection.get(0);
			ArrayList<T> next_collection = new ArrayList<T>(collection.size() - 1);
			for (int i = 1; i < collection.size(); i++) {
				T item = collection.get(i);
				next_collection.add(item);
			}
			// ArrayList<T> next_collection = (ArrayList<T>) collection.clone();
			// next_collection.remove(0);
			T result = Util.foldLeft(f, next_collection, init);
			return result;
		}
	}
	static public <T> ArrayList<T> concatenate(ArrayList<T> a, ArrayList<T> b) {
		ArrayList<T> result = new ArrayList<T>(a.size() + b.size());
		for (T value : a) {
			result.add(value);
		}
		for (T value : b) {
			result.add(value);
		}
		return result;
	}
	static public <T1, T2> ArrayList<T2> map(UnaryFunc<T1, T2> f, 
			ArrayList<T1> collection) {
		ArrayList<T2> result = new ArrayList<T2>(collection.size());
		for (T1 value : collection) {
			T2 next_value = f.call(value);
			result.add(next_value);
		}
		return result;
	}
	static public String join(ArrayList<String> collection, String separator) {
		// F4 f = new F4(separator);
		// String result = reduceLeft(f, collection);
		StringBuilder builder = new StringBuilder();
		if (collection.size() >= 1) {
			builder.append(collection.get(0));
		}
		for(int i = 1; i < collection.size(); i++) {
			String s = collection.get(i);
			builder.append(separator);
			builder.append(s);
		}
		String result = builder.toString();
		return result;
	}
	static public int sum(ArrayList<Integer> collection) {
		F7 f = new F7();
		int result = foldLeft(f, collection, 0);
		return result;
	}
}
interface BinaryFunc<V, A> {
	public A call(V a, V b);
}
interface UnaryFunc<T1, T2> {
	public T2 call (T1 a);
}
class F4 implements BinaryFunc<String, String> {
	String separator;
	public F4(String separator) {
		this.separator = separator;
	}
	public String call(String a, String b) {
		String separator = this.separator;
		// return a + separator + b;
		return a.concat(separator).concat(b);
	}
}
class F5 implements UnaryFunc<SackItem, Integer> {
	public F5() {
	}
	public Integer call(SackItem a) {
		return a.getIdentifierValue();
	}
}
class F6 implements UnaryFunc<SackItem, Integer> {
	public F6() {
	}
	public Integer call(SackItem a) {
		return a.getProfit();
	}
}
class F7 implements BinaryFunc<Integer, Integer> {
	public F7() {
	}
	public Integer call(Integer a, Integer b) {
		return a + b;
	}
}
class WeightContainer {
	int weight;
	public WeightContainer(int weight) {
		this.weight = weight;
	}
	public int getWeight() {
		return this.weight;
	}
	public void setWeight(int weight) {
		this.weight = weight;
	}
}
