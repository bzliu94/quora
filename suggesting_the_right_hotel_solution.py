# 2016-04-08

# output three most appropriate hotels for each booker

# favored cities are grouped by visit count, 
# and we consider city classes in order of visits descending

# for each favored city, unvisited hotels that are closest 
# according to feature space relative to mean of 
# previously-visited hotel features are considered

# revert to k-nn search with kd-tree and query point 
# as mean feature point when we run out of favored cities; 
# number of points to check is (at worst) 
# number of visited hotels plus original query size (three) 
# minus num. accumulated (non-visited) hotel id values 
# in current result

# this way, we are guaranteed to have three results for each booker

# for this input set, check bookers #44999939, #21239866

# inspired by pavel lepin

# deviates from pavel lepin's version due to different (arbitrary) tie-breaking

# assumes we have at least one hotel booked in past for each booker, 
# which is true for the dataset (minimum of five bookings for each booker), 
# and which is possibly reasonable as otherwise we would not have 
# a basis on which to recommend hotels given this data

from collections import defaultdict
from scipy.spatial import cKDTree
import math
import numpy
import csv
def getDistance(x1, y1, z1, x2, y2, z2):
  value = math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2)
  return value
def getRecommendedHotels(n, visited_hotel_id_list, city_count_to_city_id_list_dict, mean_stars, mean_reviews, mean_min_price, kd_tree, point_to_hotel_id_list_dict):
  result = []
  items = city_count_to_city_id_list_dict.items()
  sorted_items = sorted(items, key = lambda x: x[0], reverse = True)
  sorted_values = [x[1] for x in sorted_items]
  sorted_city_groups = sorted_values
  for city_group in sorted_city_groups:
    mergee_result = getRecommendedHotelsGivenCityGroup(n - len(result), visited_hotel_id_list + result, city_group, mean_stars, mean_reviews, mean_min_price)
    result = result + mergee_result
    if len(result) == n:
      break
  # care about adding more hotels and ran out of favored cities
  if len(result) != n:
    worst_case_close_seen_hotel_id_set = set(visited_hotel_id_list)
    worst_case_close_seen_hotel_id_list = list(worst_case_close_seen_hotel_id_set)
    worst_case_num_close_seen_hotels = len(worst_case_close_seen_hotel_id_list)
    query_result = kd_tree.query((mean_stars, mean_reviews, mean_min_price), worst_case_num_close_seen_hotels + n - len(result))
    d, i = query_result
    close_points = [tuple(kd_tree.data[int(x)]) for x in i] if isinstance(i, numpy.ndarray) else [tuple(kd_tree.data[int(i)])]
    close_hotel_id_list_list = [point_to_hotel_id_list_dict[x] for x in close_points]
    # assume no overlap in hotel id collections
    close_hotel_id_list = reduce(lambda x, y: x + y, close_hotel_id_list_list, [])
    close_non_seen_hotel_id_list = [x for x in close_hotel_id_list if x not in worst_case_close_seen_hotel_id_set]
    added_hotel_id_list = close_non_seen_hotel_id_list[ : n - len(result)]
    result = result + added_hotel_id_list
  return result
def getRecommendedHotelsGivenCityGroup(n, visited_hotel_id_list, city_id_list, mean_stars, mean_reviews, mean_min_price):
  result = getFeatureDistanceOrderedHotelsGivenCityGroup(visited_hotel_id_list, city_id_list, mean_stars, mean_reviews, mean_min_price)
  next_result = result[0 : min(n, len(result))]
  return next_result
def getFeatureDistanceOrderedHotelsGivenCityGroup(visited_hotel_id_list, city_id_list, mean_stars, mean_reviews, mean_min_price):
  result = []
  for city_id in city_id_list:
    partial_result = getFeatureDistanceTaggedHotelsGivenCity(visited_hotel_id_list, city_id, mean_stars, mean_reviews, mean_min_price)
    result = result + partial_result
  next_result = sorted(result, key = lambda x: x[0])
  next_next_result = [x[1] for x in next_result]
  return next_next_result
def getFeatureDistanceTaggedHotelsGivenCity(visited_hotel_id_list, city_id, mean_stars, mean_reviews, mean_min_price):
  result = []
  hotel_id_to_features_dict = hotel_city_id_to_hotel_id_to_hotel_features_dict[city_id]
  for hotel_id in hotel_id_to_features_dict.keys():
    features = hotel_id_to_features_dict[hotel_id]
    if hotel_id in visited_hotel_id_list:
      continue
    dist = getDistance(mean_stars, mean_reviews, mean_min_price, features.getNormalizedStars(), features.getNormalizedReviews(), features.getNormalizedMinPrice())
    curr_item = (dist, hotel_id)
    result.append(curr_item)
  return result
bookers_csv_file = open("Bookers.csv", "rb")
# bookers_csv_file = open("Bookers_44999939.csv", "rb")
bookers_reader = csv.reader(bookers_csv_file, delimiter = ",", quotechar = "|")
booking_dict_list = []
bookers_reader.next()
booker_id_set = set([])
for row in bookers_reader:
  booker_id = int(row[0])
  hotel_id = int(row[1])
  booked_date = str(row[2])
  curr_dict = {"booker_id": booker_id, "hotel_id": hotel_id, "booked_date": booked_date}
  booking_dict_list.append(curr_dict)
  booker_id_set |= set([booker_id])
booker_id_list = list(booker_id_set)
hotels_csv_file = open("Hotels.csv", "rb")
hotels_reader = csv.reader(hotels_csv_file, delimiter = ",", quotechar = "|")
hotels_reader.next()
hotel_dict_list = []
for row in hotels_reader:
  hotel_id = int(row[0])
  city_id = int(row[1])
  stars = int(row[2])
  reviews = float(row[3] if row[3] != "" else 0)
  min_price = float(row[4])
  max_price = float(row[5])
  curr_dict = {"hotel_id": hotel_id, "city_id": city_id, "stars": stars, "reviews": reviews, "min_price": min_price, "max_price": max_price}
  hotel_dict_list.append(curr_dict)
booker_id_to_hotel_id_list_dict = defaultdict(lambda: [])
for booking_dict in booking_dict_list:
  booker_id = booking_dict["booker_id"]
  hotel_id = booking_dict["hotel_id"]
  booker_id_to_hotel_id_list_dict[booker_id].append(hotel_id)
class HotelFeatures:
  def __init__(self, city_id, stars, reviews, min_price):
    self.city_id = city_id
    self.stars = stars
    self.reviews = reviews
    self.min_price = min_price
  def getFeatures(self):
    stars_normalized = self.getNormalizedStars()
    reviews_normalized = self.getNormalizedReviews()
    min_price_normalized = self.getNormalizedMinPrice()
    features = (stars_normalized, reviews_normalized, min_price_normalized)
    return features
  def getCityID(self):
    city_id = self.city_id
    return self.city_id
  def getNormalizedStars(self):
    stars_normalized = self.stars / (1.0 * 5)
    return stars_normalized
  def getNormalizedReviews(self):
    reviews_normalized = (self.reviews - 5) / (1.0 * 5)
    return reviews_normalized
  def getNormalizedMinPrice(self):
    min_price_normalized = self.min_price / (1.0 * 100) if self.min_price <= 1000 else 0
    return min_price_normalized
hotel_id_to_hotel_features_dict = {}
hotel_city_id_to_hotel_id_to_hotel_features_dict = defaultdict(lambda: {})
for hotel_dict in hotel_dict_list:
  hotel_id = hotel_dict["hotel_id"]
  hotel_features = HotelFeatures(hotel_dict["city_id"], hotel_dict["stars"], hotel_dict["reviews"], hotel_dict["min_price"])
  hotel_id_to_hotel_features_dict[hotel_id] = hotel_features
  hotel_city_id_to_hotel_id_to_hotel_features_dict[hotel_dict["city_id"]][hotel_dict["hotel_id"]] = hotel_features
point_to_hotel_id_list_dict = defaultdict(lambda: [])
data = []
for hotel_dict in hotel_dict_list:
  hotel_id = hotel_dict["hotel_id"]
  hotel_features = hotel_id_to_hotel_features_dict[hotel_id]
  hotel_feature_vec = hotel_features.getFeatures()
  data.append(hotel_feature_vec)
  point_to_hotel_id_list_dict[hotel_feature_vec].append(hotel_id)
kd_tree = cKDTree(data)
print "user_id,rec_hotel_1,rec_hotel_2,rec_hotel_3"
def getDistanceTaggedHotelIDValues(hotel_id_list, hotel_id_to_hotel_features_dict, stars, reviews, min_price):
  feature_obj_list = [hotel_id_to_hotel_features_dict[x] for x in hotel_id_list]
  distances = [getDistance(stars, reviews, min_price, x.getNormalizedStars(), x.getNormalizedReviews(), x.getNormalizedMinPrice()) for x in feature_obj_list]
  result = [(distances[i], hotel_id_list[i]) for i in xrange(len(hotel_id_list))]
  return result
for booker_id in booker_id_list:
  hotel_id_list = booker_id_to_hotel_id_list_dict[booker_id]
  hotel_feature_obj_list = [hotel_id_to_hotel_features_dict[x] for x in hotel_id_list]
  # use this dict. later by inverting it
  city_id_to_count_dict = defaultdict(lambda: 0)
  num_previously_visited_hotels = len(hotel_id_list)
  mean_stars = 0
  mean_reviews = 0
  mean_min_price = 0
  for hotel_feature_obj in hotel_feature_obj_list:
    mean_stars += hotel_feature_obj.getNormalizedStars()
    mean_reviews += hotel_feature_obj.getNormalizedReviews()
    mean_min_price += hotel_feature_obj.getNormalizedMinPrice()
    city_id_to_count_dict[hotel_feature_obj.getCityID()] += 1
  city_count_to_city_id_list_dict = defaultdict(lambda: [])
  for city_id in city_id_to_count_dict.keys():
    count = city_id_to_count_dict[city_id]
    city_count_to_city_id_list_dict[count].append(city_id)
  mean_stars /= num_previously_visited_hotels
  mean_reviews /= num_previously_visited_hotels
  mean_min_price /= num_previously_visited_hotels
  recommended_hotel_id_values = getRecommendedHotels(3, hotel_id_list, city_count_to_city_id_list_dict, mean_stars, mean_reviews, mean_min_price, kd_tree, point_to_hotel_id_list_dict)
  recommended_hotel_id_str_list = [str(x) for x in recommended_hotel_id_values]
  booker_id_str = str(booker_id)
  result_str = booker_id_str + "," + ",".join(recommended_hotel_id_str_list)
  print result_str
