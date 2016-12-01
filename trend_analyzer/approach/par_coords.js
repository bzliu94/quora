EMPTY_STR = ""

// if a column has all EMPTY values, then it is removed because an empty column is a string column and for string columns we require at least two non-EMPTY values to have it survive

// BL - only converts given values if they are interval strings and we return a numerical value

function idempotentParsePossibleIntervalStrIntoMidpoint(value, pc, column_name) {
    // console.log("column name:", column_name, pc["column_name_to_column_num_dict"]())
    column_num = pc["column_name_to_column_num_dict"]()[column_name]
    var next_val = 0;
    // console.log(pc["condensed_column_is_date_range_type_list"]()[column_num])
    if (pc["condensed_column_is_date_range_type_list"]()[column_num] == true) {
	// BL - value is a date range
	// BL - added midpoint date logic
	// var date_range_str = "05/06/2000 08:00 AM +0000...09/24/2009 10:09 PM +0000"
	// console.log(column_num, column_name, value, pc["condensed_column_is_date_range_type_list"]())
	// throw "whoops"
	var date_range_str = value
	var split_date_str_list = date_range_str.split("...")
	var date_start_str = split_date_str_list[0]
	var date_end_str = split_date_str_list[1]
	var date_start = new Date(date_start_str)
	var date_end = new Date(date_end_str)
	var date_start_sec = date_start.getTime() / 1000
	var date_end_sec = date_end.getTime() / 1000
	var mid_date_sec = (date_start_sec + date_end_sec) / 2
	var mid_date = new Date(mid_date_sec * 1000)
	// console.log(mid_date)
	next_val = mid_date.getTime();
    } else if (typeof value === "string" && value.split("...").length == 2 && pc["condensed_column_is_quant_type_list"]()[column_num] == true) {
	var arr = pc.toIntervalFloatArray(value);
	var l = arr[0];
	var r = arr	[1];
	var m = (l + r) / 2.0;
	next_val = m;
    } else {
	// BL - had a bug here where we need parseFloat()
	if (typeof value === "string" && isNaN(parseFloat(value)) == false) {
	    // next_val = parseFloat(value)
	    next_val = value
	} else {
	    // console.log(value)
	    next_val = value;
	}
	// console.log(typeof next_val)
    }
    /*
      if (next_val == null) {
      console.log("found a null value");
      }
    */

    /*

      if (isNaN(next_val) == true) {

      console.log(next_val)

      console.log("found a problem");

      }

    */

    return next_val;
}


// d[k] is [x_non_scaled, y_non_scaled (possibly NaN), attribute string (possibly interval string), optional attribute name string (for if we are dealing with an interval attribute)

// y_scale is a function that determines scaled y upon application

// converts interval strings to numerical values and scales

function intervalStrToMidpoint(d_k, pc, do_scale) {

    var val = 0;
    // console.log(d_k[3])
    column_name = d_k[3]
    column_num = pc["column_name_to_column_num_dict"]()[column_name]
    is_date_range = pc["condensed_column_is_date_range_type_list"]()[column_num]
    // is_percent_range = pc["condensed_column_is_percent_type_list"]()[column_num]
    // console.log(is_date_range, column_name,
    if (is_date_range == true) {
	// assume unscaled y is already a date object
	// val = d_k[2]
	// console.log(val)
	// console.log(d_k[2])
	if (d_k[2] instanceof Date) {
	  val = d_k[2]
	} else if (parseFloat(d_k[2]) == d_k[2]) {
	  // console.log(d_k[2])
	  val = d_k[2]
	} else {
	  val = idempotentParsePossibleIntervalStrIntoMidpoint(d_k[2], pc, column_name)
	}
	if (do_scale == true) {
	    // 																																																																																																																																																																																																																																																																																																																																																																																																																			console.log(pc.yscale, d_k[3])
	    val = pc.yscale[d_k[3]](val);
	}
	// console.log(val)
	// if (typeof d_k[2] === "string") throw "string provided, though the method name implies it is okay"
	// console.log(d_k[2])
	// console.log(val)
    // BL - requiring that we're for a quantitative attribute here fixes case when attribute is categorical; points show up
    } else if (typeof d_k[2] === "string" && d_k[2].split("...").length == 2 && pc["condensed_column_is_quant_type_list"]()[column_num] == true) {
	// we are dealing with an interval attribute; retrieve midpoint and transform
	// BL - most of the time, we have already called idempotentParsePossibleIntervalStrIntoMidpoint() to determine d_k[1], which is unscaled_y; but in that case, the value would no longer be a string, and as a number, it passes through
	var arr = pc.toIntervalFloatArray(d_k[2]);
	var l = arr[0];
	var r = arr[1];
	var m = (l + r) / 2.0;
	if (do_scale == true) {
	    val = pc.yscale[d_k[3]](m);
	} else {
	    val = m;
	}
    } else if (typeof d_k[2] === "string" && isNaN(parseFloat(d_k[2])) == false) {
	// console.log(d_k[2], d_k[2].split("..."), pc["condensed_column_is_quant_type_list"]()[column_num], column_name)
	// BL - had a bug here where we need parseFloat()
	// var curr_val = parseFloat(d_k[2])
	var curr_val = d_k[2]
	if (do_scale == true) {
	    val = pc.yscale[d_k[3]](curr_val);
	    // console.log(val)
	} else {
	    val = curr_val;
	}
    } else if (d_k[2] === undefined) {
	// BL - i'm not sure why we have to handle this here
	val = d_k[2]
    } else {
	// var curr_val = parseFloat(interval_str);
	// val = pc.toTypeCoerceNumbers(interval_str) === "string" ? interval_str : curr_val
	// y_scaled is well-formed; return it
	if (do_scale == true) {
	    // console.log(pc.yscale, d_k[3])
	    val = pc.yscale[d_k[3]](d_k[2]);
	    // console.log(val)
	} else {
	    val = d_k[2];
	}

	// note that, e.g. "a" is not a number, so isNaN("a") is true

	/*

	  if (isNaN(val) == true) {

	  console.log(val)

	  console.log("found a problem");

	  }

	*/

    }

    /*

      if (typeof val == "undefined") {
      console.log("undefined type")
      }

      console.log(typeof val)

    */

    return val;

}

d3.parcoords = function(config) {
    var __ = {
	data: [],
	highlighted: [],
	dimensions: [],
	dimensionTitles: {},
	dimensionTitleRotation: 0,
	types: {},
	brushed: false,
	mode: "default",
	rate: 20,
	width: 600,
	height: 300,
	margin: { top: 30, right: 0, bottom: 12, left: 0 },
	color: "#069",
	composite: "source-over",
	alpha: 0.7,
	bundlingStrength: 0.5,
	bundleDimension: null,
	smoothness: 0.25,
	showControlPoints: false,
	hideAxis : []
    };

    extend(__, config);
    var pc = function(selection) {
	selection = pc.selection = d3.select(selection);

	__.width = selection[0][0].clientWidth;
	__.height = selection[0][0].clientHeight;

	// canvas data layers
	["shadows", "marks", "foreground", "highlight"].forEach(function(layer) {
	    canvas[layer] = selection
		.append("canvas")
		.attr("class", layer)[0][0];
	    ctx[layer] = canvas[layer].getContext("2d");
	});

	// svg tick and brush layers
	pc.svg = selection
	    .append("svg")
	    .attr("width", __.width)
	    .attr("height", __.height)
	    .append("svg:g")
	    .attr("transform", "translate(" + __.margin.left + "," + __.margin.top + ")");

	return pc;
    };
    var events = d3.dispatch.apply(this,["render", "resize", "highlight", "brush", "brushend", "axesreorder"].concat(d3.keys(__))),
	w = function() { return __.width - __.margin.right - __.margin.left; },
	h = function() { return __.height - __.margin.top - __.margin.bottom; },
	flags = {
	    brushable: false,
	    reorderable: false,
	    axes: false,
	    interactive: false,
	    shadows: false,
	    debug: false
	},
	xscale = d3.scale.ordinal(),
	yscale = {},
	dragging = {},
	line = d3.svg.line(),
	axis = d3.svg.axis().orient("left").ticks(5),
	g, // groups for axes, brushes
	ctx = {},
	canvas = {},
	clusterCentroids = [];

    // side effects for setters
    var side_effects = d3.dispatch.apply(this,d3.keys(__))
	.on("composite", function(d) { ctx.foreground.globalCompositeOperation = d.value; })
	.on("alpha", function(d) { ctx.foreground.globalAlpha = d.value; })
	.on("width", function(d) { pc.resize(); })
	.on("height", function(d) { pc.resize(); })
	.on("margin", function(d) { pc.resize(); })
	.on("rate", function(d) { rqueue.rate(d.value); })
	.on("data", function(d) {
	    if (flags.shadows){paths(__.data, ctx.shadows);}
	})
	.on("dimensions", function(d) {
            // console.log(__)
            // console.log(__.dimensions)
	    xscale.domain(__.dimensions);
	    if (flags.interactive){pc.render().updateAxes();}
	})
	.on("bundleDimension", function(d) {
	    if (!__.dimensions.length) pc.detectDimensions();
	    if (!(__.dimensions[0] in yscale)) pc.autoscale();
	    if (typeof d.value === "number") {
		if (d.value < __.dimensions.length) {
		    __.bundleDimension = __.dimensions[d.value];
		} else if (d.value < __.hideAxis.length) {
		    __.bundleDimension = __.hideAxis[d.value];
		}
	    } else {
		__.bundleDimension = d.value;
	    }

	    __.clusterCentroids = compute_cluster_centroids(__.bundleDimension);
	})
	.on("hideAxis", function(d) {
	    if (!__.dimensions.length) pc.detectDimensions();
	    pc.dimensions(without(__.dimensions, d.value));
	});

    // expose the state of the chart
    pc.state = __;
    pc.flags = flags;

    // create getter/setters
    getset(pc, __, events);

    // expose events
    d3.rebind(pc, events, "on");

    // tick formatting
    d3.rebind(pc, axis, "ticks", "orient", "tickValues", "tickSubdivide", "tickSize", "tickPadding", "tickFormat");

    // getter/setter with event firing
    function getset(obj,state,events)  {
	d3.keys(state).forEach(function(key) {
	    obj[key] = function(x) {
		if (!arguments.length) {
		    return state[key];
		}
		var old = state[key];
		state[key] = x;
		side_effects[key].call(pc,{"value": x, "previous": old});
		events[key].call(pc,{"value": x, "previous": old});
		return obj;
	    };
	});
    };

    function extend(target, source) {
	for (key in source) {
	    target[key] = source[key];
	}
	return target;
    };

    function without(arr, item) {
	return arr.filter(function(elem) { return item.indexOf(elem) === -1; })
    };
    // BL - this is where we set scale domain
    pc.autoscale = function() {
	// yscale
	var defaultScales = {
	    "date-range": function(k) {
		return d3.time.scale()
		    .domain(d3.extent(__.data.filter(function(d) { return d[k] !== EMPTY_STR }), function(d) {
			// console.log(idempotentParsePossibleIntervalStrIntoMidpoint(d[k], pc, k))
			// console.log(d[k])
			if (d[k]) {
				curr_date = idempotentParsePossibleIntervalStrIntoMidpoint(d[k], pc, k)
				curr_date = intervalStrToMidpoint([null, curr_date, d[k], k], pc, false)
				// console.log(d[k], curr_date)
				return curr_date
			} else {
				return null
			}
			// return d[k] ? d[k].getTime() : null;
		    }))
		    .range([h()+1, 1]);
	    }, 
	    "date": function(k) {
		return d3.time.scale()
		    .domain(d3.extent(__.data, function(d) {
			return d[k] ? d[k].getTime() : null;
		    }))
		    .range([h()+1, 1]);
	    },
	    "number": function(k) {
		return d3.scale.linear()
                    // BL - tricky conversion to integer here with +d[k]
                    // BL - magic word "EMPTY" used here
		    .domain(d3.extent(__.data.filter(function(d) { /* console.log(d[k]); */ return !(d[k] === EMPTY_STR) }), function(d) { return +d[k]; }))
		    .range([h()+1, 1]);
	    },
	    // BL - added 'interval' type
	    "interval": function(k) {
		// console.log("k:" + k);
		/*
		console.log(d3.extent(__.data.filter(function(d) { return !(d[k] === EMPTY_STR) }), function(d) { 
			// var val = intervalStrToMidpoint([null, yscale[p](d[p]), d[p], p], pc, true);
			var unscaled_y = idempotentParsePossibleIntervalStrIntoMidpoint(d[k], pc);
			return intervalStrToMidpoint([null, unscaled_y, d[k], k], pc, false); 
		    }))
		*/
		var result = d3.scale.linear()
		// d[k]
                    // BL - magic word "EMPTY" used here
		    // BL - range changing occurs here; modify this for percent attributes
		    .domain(d3.extent(__.data.filter(function(d) { /* console.log(d[k]); */ return !(d[k] === EMPTY_STR) }), function(d) { 
			// var val = intervalStrToMidpoint([null, yscale[p](d[p]), d[p], p], pc, true);
			var unscaled_y = idempotentParsePossibleIntervalStrIntoMidpoint(d[k], pc, k);
			return intervalStrToMidpoint([null, unscaled_y, d[k], k], pc, false); 
//		    }).map(function(x, i) { if (i == 0) return 0; else if (i == 1) return 100; }))
		    }).map(function(x, i) {
				// console.log(k)
				// console.log(__["column_name_to_column_num_dict"], k)
				column_num = __["column_name_to_column_num_dict"][k]
				is_percent_type = __["condensed_column_is_percent_type_list"][column_num]
				// return x
				if (is_percent_type) {
					if (i == 0) {
						return 0;
					} else if (i == 1) {
						return 100;
					}
				} else {
					return x;
				}
				}))
		    .range([h() + 1, 1]);
		// console.log(result);
		return result;
	    },
	    "string": function(k) {
		// console.log(k);
		var counts = {},
		    domain = [];

		// Let's get the count for each value so that we can sort the domain based
		// on the number of items for each value.
		__.data.map(function(p) {
		    // console.log(p);
		    if (counts[p[k]] === undefined) {
			counts[p[k]] = 1;
		    } else {
			counts[p[k]] = counts[p[k]] + 1;
		    }
		});

		domain = Object.getOwnPropertyNames(counts).sort(function(a, b) {
		    // return counts[a] - counts[b];
		    // BL - alphabetical ordering
		    return a < b;
		});

		// domain = domain.filter(function(d) { return d != EMPTY_STR; })

		// console.log(domain, EMPTY_STR, 1)

		return d3.scale.ordinal()
                    // BL - magic word "EMPTY" used here
		    .domain(domain.filter(function(d) { /* console.log(d[k]); */ return d !== EMPTY_STR }))
		    .rangePoints([h()+1, 1]);
	    }
	};

	__.dimensions.forEach(function(k) {
	    // console.log(k, __.types[k])
	    yscale[k] = defaultScales[__.types[k]](k);
	});

	__.hideAxis.forEach(function(k) {
	    yscale[k] = defaultScales[__.types[k]](k);
	});

        // BL - if this removes a dimension, bugs may occur

	// hack to remove ordinal dimensions with many values
	pc.dimensions(pc.dimensions().filter(function(p,i) {
	    var uniques = yscale[p].domain().length;
	    if (__.types[p] == "string" && (uniques > 60 || uniques < 1)) {
		return false;
	    }
	    return true;
	}));

	// xscale
	xscale.rangePoints([0, w()], 1);

	// canvas sizes
	pc.selection.selectAll("canvas")
	    .style("margin-top", __.margin.top + "px")
	    .style("margin-left", __.margin.left + "px")
	    .attr("width", w()+2)
	    .attr("height", h()+2);

	// default styles, needs to be set when canvas width changes
        // console.log(ctx)
	ctx.foreground.strokeStyle = __.color;
	ctx.foreground.lineWidth = 1.4;
	ctx.foreground.globalCompositeOperation = __.composite;
	ctx.foreground.globalAlpha = __.alpha;
	ctx.highlight.lineWidth = 3;
	ctx.shadows.strokeStyle = "#dadada";

	return this;
    };

    pc.scale = function(d, domain) {
	yscale[d].domain(domain);

	return this;
    };

    pc.flip = function(d) {
	//yscale[d].domain().reverse();					// does not work
	yscale[d].domain(yscale[d].domain().reverse()); // works

	return this;
    };

    // BL - doesn't work with 'interval' type

    pc.commonScale = function(global, type) {
	var t = type || "number";
	if (typeof global === 'undefined') {
	    global = true;
	}

	// scales of the same type
	var scales = __.dimensions.concat(__.hideAxis).filter(function(p) {
	    return __.types[p] == t;
	});

	if (global) {
	    var extent = d3.extent(scales.map(function(p,i) {
		return yscale[p].domain();
	    }).reduce(function(a,b) {
		return a.concat(b);
	    }));

	    scales.forEach(function(d) {
		yscale[d].domain(extent);
	    });

	} else {
	    scales.forEach(function(k) {
		yscale[k].domain(d3.extent(__.data, function(d) { return +d[k]; }));
	    });
	}

	// update centroids
	if (__.bundleDimension !== null) {
	    pc.bundleDimension(__.bundleDimension);
	}

	return this;
    };
    pc.detectDimensions = function() {
	pc.types(pc.detectDimensionTypes(__.data));
	pc.dimensions(d3.keys(pc.types()));
	return this;
    };

    // a better "typeof" from this post: http://stackoverflow.com/questions/7390426/better-way-to-get-type-of-a-javascript-variable
    pc.toType = function(v) {
	var val = ({}).toString.call(v).match(/\s([a-zA-Z]+)/)[1].toLowerCase();
	/*
	  if (val == null) {
	  console.log("problem encountered");
	  }
	*/
	return val;
    };

    pc.toIntervalFloatArray = function(v) {
	return v.split("...").map(function(x) { return parseFloat(x); });
    };

    // try to coerce to number before returning type
    pc.toTypeCoerceNumbers = function(v, column_name) {
	// console.log(__["column_name_to_column_num_dict"], this.condensed_column_is_quant_type_list(), column_name)
	col = __["column_name_to_column_num_dict"][column_name]
	// v = new Date("10/27/2009 06:00 PM +0000")
	// console.log(this.condensed_column_is_quant_type_list()[col], col)
	if (__["condensed_column_is_date_range_type_list"][col] == true) {
	    // console.log(__["condensed_column_is_date_range_type_list"], col)
	    return "date-range"
        } else if (this.condensed_column_is_quant_type_list()[col] == false) {
	    // BL - if column is categorical (e.g. a numeric category like a meeting room number), 
	    //   we have a string
	    // console.log("hello")
	    return "string"
	} else if ((parseFloat(v) == v) && (v != null)) {
	    return "number";
	    // BL - added 'interval' type; this is crude
	} else if (typeof v == "string" && v.split("...").length == 2) {
            // console.log("hello");
            return "interval";
	} else {
            // BL - can, e.g., return "string" or "date"
            result = pc.toType(v);
	    return result;
	}
    };

    // BL - note - this is where we set dimension types

    // attempt to determine types of each dimension based on first row of data
    pc.detectDimensionTypes = function(data) {
	var types = {};
	d3.keys(data[0])
	    .forEach(function(col) {
                // BL - default type, in lieu of evidence, is string
                var type = "string"
                for (var i = 0; i < data.length; i++) {
                  // BL - magic word "EMPTY" is used
                  if ((data[i][col] === EMPTY_STR) == false) {
                    type = pc.toTypeCoerceNumbers(data[i][col], col)
                  }
                }
                types[col] = type
		// types[col] = pc.toTypeCoerceNumbers(data[0][col]);
	    });
	return types;
    };
    pc.render = function() {

	// console.log("hello", __.dimensions, yscale)

	// try to autodetect dimensions and create scales
	if (!__.dimensions.length) {
		// console.log("1")
		pc.detectDimensions();
	}
	if (!(__.dimensions[0] in yscale)) {
		// console.log("2")
		pc.autoscale();
	}

	pc.render[__.mode]();

	events.render.call(this);
	return this;
    };

    pc.render['default'] = function() {
	pc.clear('foreground');
	if (__.brushed) {
	    __.brushed.forEach(path_foreground);
	    __.highlighted.forEach(path_highlight);
	} else {
	    __.data.forEach(path_foreground);
	    __.highlighted.forEach(path_highlight);
	}
    };

    var rqueue = d3.renderQueue(path_foreground)
	.rate(50)
	.clear(function() {
	    pc.clear('foreground');
	    pc.clear('highlight');
	});

    pc.render.queue = function() {
	if (__.brushed) {
	    rqueue(__.brushed);
	    __.highlighted.forEach(path_highlight);
	} else {
	    // BL - this is where we add lines
	    // k is column, p is row
	    /*
	      next_data = __.data.map(function(p) {
	      console.log(p)
	      if (p[2].split("...").length == 2) {
              var result = p;
              var arr = pc.toIntervalFloatArray(val);
              var l = arr[0];
              var r = arr[1];
              var m = (l + r) / 2.0;
              result[1] = m;
              return result;
	      } else {
              return p;
	      }
	      })
	      rqueue(next_data);
	    */
	    rqueue(__.data);
	    __.highlighted.forEach(path_highlight);

	}

    };
    function compute_cluster_centroids(d) {

	var clusterCentroids = d3.map();
	var clusterCounts = d3.map();
	// determine clusterCounts
	__.data.forEach(function(row) {
	    var scaled = yscale[d](row[d]);
	    if (!clusterCounts.has(scaled)) {
		clusterCounts.set(scaled, 0);
	    }
	    var count = clusterCounts.get(scaled);
	    clusterCounts.set(scaled, count + 1);
	});

	__.data.forEach(function(row) {
	    __.dimensions.map(function(p, i) {
		var scaled = yscale[d](row[d]);
		if (!clusterCentroids.has(scaled)) {
		    var map = d3.map();
		    clusterCentroids.set(scaled, map);
		}
		if (!clusterCentroids.get(scaled).has(p)) {
		    clusterCentroids.get(scaled).set(p, 0);
		}
		var value = clusterCentroids.get(scaled).get(p);
		value += yscale[p](row[p]) / clusterCounts.get(scaled);
		clusterCentroids.get(scaled).set(p, value);
	    });
	});

	return clusterCentroids;

    }

    // BL - modified this to deal with NaN problem for interval attributes
    // BL - need to modify this to have proper axis dots as well

    function compute_centroids(row) {
	var centroids = [];

	var p = __.dimensions;
	var cols = p.length;
	var a = 0.5;			// center between axes
	for (var i = 0; i < cols; ++i) {
	    // centroids on 'real' axes
	    var x = position(p[i]);
            // console.log(x)
	    // var y = yscale[p[i]](row[p[i]]);
            // console.log(row[p[i]])
            // BL - this change may break things
            if (row[p[i]] === EMPTY_STR) {
              continue
            }
            // BL - note that y is sometimes NaN for numeric attributes when we have a gap
            // BL - change here
	    // console.log(__["condensed_column_names"][i])
            var y = intervalStrToMidpoint([null, idempotentParsePossibleIntervalStrIntoMidpoint(row[p[i]], pc, __["condensed_column_names"][i]), row[p[i]], p[i]], pc, true);
	    // console.log(__["condensed_column_is_date_range_type_list"][i], x, y)
	    // console.log(__["condensed_column_is_percent_type_list"][i], x, y, idempotentParsePossibleIntervalStrIntoMidpoint(row[p[i]], pc, __["condensed_column_names"][i]))
	    centroids.push([x, y, i]);
	    //centroids.push($V([x, y]));

	    // centroids on 'virtual' axes
	    if (i < cols - 1) {
		var cx = x + a * (position(p[i+1]) - x);
		// var cy = y + a * (yscale[p[i+1]](row[p[i+1]]) - y);
		// console.log(__["condensed_column_names"][i + 1])
                var cy = y + a * intervalStrToMidpoint([null, idempotentParsePossibleIntervalStrIntoMidpoint(row[p[i + 1]], pc, __["condensed_column_names"][i + 1]), row[p[i + 1]], p[i + 1]], pc, true);
		if (__.bundleDimension !== null) {
		    var leftCentroid = __.clusterCentroids.get(yscale[__.bundleDimension](row[__.bundleDimension])).get(p[i]);
		    var rightCentroid = __.clusterCentroids.get(yscale[__.bundleDimension](row[__.bundleDimension])).get(p[i+1]);
		    var centroid = 0.5 * (leftCentroid + rightCentroid);
		    cy = centroid + (1 - __.bundlingStrength) * (cy - centroid);
		}
		centroids.push([cx, cy, i]);
		//centroids.push($V([cx, cy]));
	    }
	}
	/*
	  var next_centroids = centroids.filter(function(x) { return isNaN(x[1]); });
	  if (next_centroids.length > 0) {
	  console.log("have yet another problem");
	  }
	*/
	/*
          if (x == null) {
          console.log("have a problem");
          }
	*/

	return centroids;
    }

    pc.compute_centroids = compute_centroids;

    function compute_control_points(centroids) {

	var cols = centroids.length;
	var a = __.smoothness;
	var cps = [];

	cps.push(centroids[0]);
	cps.push($V([centroids[0].e(1) + a*2*(centroids[1].e(1)-centroids[0].e(1)), centroids[0].e(2)]));
	for (var col = 1; col < cols - 1; ++col) {
	    var mid = centroids[col];
	    var left = centroids[col - 1];
	    var right = centroids[col + 1];

	    var diff = left.subtract(right);
	    cps.push(mid.add(diff.x(a)));
	    cps.push(mid);
	    cps.push(mid.subtract(diff.x(a)));
	}
	cps.push($V([centroids[cols-1].e(1) + a*2*(centroids[cols-2].e(1)-centroids[cols-1].e(1)), centroids[cols-1].e(2)]));
	cps.push(centroids[cols - 1]);

	return cps;

    };

    pc.shadows = function() {
	flags.shadows = true;
	if (__.data.length > 0) {
	    paths(__.data, ctx.shadows);
	}
	return this;
    };

    // draw little dots on the axis line where data intersects
    pc.axisDots = function(data) {
	var ctx = pc.ctx.marks;
	ctx.globalAlpha = d3.min([ 1 / Math.pow(data.length, 1 / 2), 1 ]);
	__.data.forEach(function(d) {
	    __.dimensions.map(function(p, i) {

			// console.log(p)
			var unscaled_y = idempotentParsePossibleIntervalStrIntoMidpoint(d[p], pc, p);
			var scaled_y = intervalStrToMidpoint([null, unscaled_y, d[p], p], pc, true);
		/*
		if (d[p] == 0) {
			console.log(d[p])
		}
		*/
		if (d[p] === EMPTY_STR) {
			// BL - null minus a number is a number, so watch out for that
			// console.log(d[p])
			return;
		} else {
			// ctx.fillRect(position(p) - 0.75, yscale[p](d[p]) - 0.75, 5, 5);
			ctx.fillRect(position(p) - 2.5, scaled_y - 2.5, 5, 5);
                	// console.log(d, p, i, d[p], yscale[p], position(p), yscale[p](d[p]))
		}
	    });
	});
	return this;
    };

    // draw single cubic bezier curve
    function single_curve(d, ctx) {

        // BL - this is likely broken because we have three-tuples for compute_centroids() now
	var centroids = compute_centroids(d);
	var cps = compute_control_points(centroids);

	ctx.moveTo(cps[0].e(1), cps[0].e(2));
	for (var i = 1; i < cps.length; i += 3) {
	    if (__.showControlPoints) {
		for (var j = 0; j < 3; j++) {
		    ctx.fillRect(cps[i+j].e(1), cps[i+j].e(2), 2, 2);
		}
	    }
	    ctx.bezierCurveTo(cps[i].e(1), cps[i].e(2), cps[i+1].e(1), cps[i+1].e(2), cps[i+2].e(1), cps[i+2].e(2));
	}
    };

    // draw single polyline
    function color_path(d, i, ctx) {
	ctx.strokeStyle = d3.functor(__.color)(d, i);
        // console.log(ctx.strokeStyle);
	ctx.beginPath();
	if (__.bundleDimension === null || (__.bundlingStrength === 0 && __.smoothness == 0)) {
	    single_path(d, ctx);
	} else {
	    single_curve(d, ctx);
	}
	ctx.stroke();
    };

    // draw many polylines of the same color
    function paths(data, ctx) {
	ctx.clearRect(-1, -1, w() + 2, h() + 2);
	ctx.beginPath();
	data.forEach(function(d) {
	    if (__.bundleDimension === null || (__.bundlingStrength === 0 && __.smoothness == 0)) {
		single_path(d, ctx);
	    } else {
		single_curve(d, ctx);
	    }
	});
	ctx.stroke();
    };

    function single_path(d, ctx) {
        // var prev_column_name = null
        // var prev_stroke_style = null
        var prev_stroke_style = null
	var prev_line_width = ctx.lineWidth
	var prev_gco = ctx.globalCompositeOperation
	var prev_global_alpha = ctx.globalAlpha
        // var prev_axis_had_empty = false
	__.dimensions.map(function(p, i) {
	    // BL - prev_stroke_style is used to store non-dash color
	    prev_stroke_style = d3.functor(__.color)(d, i)
            // console.log(position(p));
            // console.log([d, p, i]);
            // BL - this is where positions for segments are determined
            // console.log([position(p), yscale[p](d[p])]);
            // d[p] is an attribute value for attribute name p
            // yscale[p] is y-scaler function that takes a value in domain (possibly a string for a categorical attribute or a midpoint for an interval attribute
            // var val = intervalStrToMidpoint(d[p], pc);
	    // console.log(d[p], p)
            var val = intervalStrToMidpoint([null, idempotentParsePossibleIntervalStrIntoMidpoint(d[p], pc, p), d[p], p], pc, true);
            // console.log(d[p]);
            // console.log(d, p, i, prev_column_name)
            // BL - magic word "EMPTY" is used
            // if (d[p] === "EMPTY" || (prev_column_name != null && d[prev_column_name] === "EMPTY")) {
            if (d[p] === EMPTY_STR) {
              // empty cell; ignore this axis
              // prev_axis_had_empty = true
              // prev_stroke_style = ctx.strokeStyle
              ctx.setLineDash([5])
              ctx.strokeStyle = "silver"
              // ctx.moveTo(position(p), val);
              return
            } else {
	    if (i == 0) {
                // ctx.moveTo(position(p), yscale[p](val));
		ctx.strokeStyle = prev_stroke_style
                ctx.setLineDash([])
		ctx.moveTo(position(p), val);
	    } else {
                // ctx.lineTo(position(p), yscale[p](val));
                // BL - in order for line segments to have different styles, we have to finish a stroke (and start a new
		ctx.lineTo(position(p), val);
                ctx.stroke()
                ctx.beginPath()
                ctx.moveTo(position(p), val)
                ctx.strokeStyle = prev_stroke_style
                ctx.lineWidth = prev_line_width
                ctx.globalCompositeOperation = prev_gco
                ctx.globalAlpha = prev_global_alpha
                // console.log(ctx.strokeStyle)
                ctx.setLineDash([])
                // ctx.strokeStyle = prev_stroke_style
	    }
	    }
            // prev_column_name = p
	});
    }

    function path_foreground(d, i) {
        // console.log([d, i]);
	var value = color_path(d, i, ctx.foreground);
            // BL - moved adding axis dots to here, which is slightly better than adding them all at beginning (before adding any line segment); brute-forcing it and inefficient
            // console.log(__.data)
            pc.axisDots(__.data)
        return value;
    };

    function path_highlight(d, i) {
	var value = color_path(d, i, ctx.highlight);
            // BL - moved adding axis dots to here as well, which is slightly better than adding them all at beginning (before adding any line segment); brute-forcing it and inefficient
            // console.log(__.data)
            pc.axisDots(__.data)
        return value;
    };
    pc.clear = function(layer) {
	ctx[layer].clearRect(0,0,w()+2,h()+2);
	return this;
    };
    function flipAxisAndUpdatePCP(dimension, i) {
	var g = pc.svg.selectAll(".dimension");

	pc.flip(dimension);
	d3.select(g[0][i])
	    .transition()
	    .duration(1100)
	    .call(axis.scale(yscale[dimension]));

	pc.render();
	if (flags.shadows) paths(__.data, ctx.shadows);
    }

    function rotateLabels() {
	var delta = d3.event.deltaY;
	delta = delta < 0 ? -5 : delta;
	delta = delta > 0 ? 5 : delta;

	__.dimensionTitleRotation += delta;
	pc.svg.selectAll("text.label")
	    .attr("transform", "translate(0,-5) rotate(" + __.dimensionTitleRotation + ")");
	d3.event.preventDefault();
    }

    // BL - this is where we set axes

    pc.createAxes = function() {
	if (g) pc.removeAxes();

	// Add a group element for each dimension.
	g = pc.svg.selectAll(".dimension")
	    .data(__.dimensions, function(d) { return d; })
	    .enter().append("svg:g")
	    .attr("class", "dimension")
	    .attr("transform", function(d) { return "translate(" + xscale(d) + ")"; });

	// Add an axis and title.
	g.append("svg:g")
	    .attr("class", "axis")
	    .attr("transform", "translate(0,0)")
	    .each(function(d) { d3.select(this).call(axis.scale(yscale[d])); })
		.append("svg:text")
	    .attr({
		"text-anchor": "middle",
		"y": 0,
		"transform": "translate(0,-5) rotate(" + __.dimensionTitleRotation + ")",
		"x": 0,
		"class": "label"
	    })
	    .text(function(d) {
		return d in __.dimensionTitles ? __.dimensionTitles[d] : d;  // dimension display names
	    })
	    .on("dblclick", flipAxisAndUpdatePCP)
	    .on("wheel", rotateLabels);

	flags.axes= true;
	return this;
    };

    pc.removeAxes = function() {
	g.remove();
	return this;
    };

    pc.updateAxes = function() {
	var g_data = pc.svg.selectAll(".dimension").data(__.dimensions);

	// console.log(g_data);

	// Enter
	g_data.enter().append("svg:g")
	    .attr("class", "dimension")
	    .attr("transform", function(p) { return "translate(" + position(p) + ")"; })
	    .style("opacity", 0)
	    .append("svg:g")
	    .attr("class", "axis")
	    .attr("transform", "translate(0,0)")
	    .each(function(d) { d3.select(this).call(function() { axis.scale(yscale[d]) }); })
		.append("svg:text")
	    .attr({
		"text-anchor": "middle",
		"y": 0,
		"transform": "translate(0,-5) rotate(" + __.dimensionTitleRotation + ")",
		"x": 0,
		"class": "label"
	    })
	    .text(String)
	    .on("dblclick", flipAxisAndUpdatePCP)
	    .on("wheel", rotateLabels);

	// Update
	g_data.attr("opacity", 0);
	g_data.select(".axis")
	    .transition()
	    .duration(1100)
	    .each(function(d) {
		d3.select(this).call(axis.scale(yscale[d]));
	    });
	g_data.select(".label")
	    .transition()
	    .duration(1100)
	    .text(String)
	    .attr("transform", "translate(0,-5) rotate(" + __.dimensionTitleRotation + ")");

	// Exit
	g_data.exit().remove();

	g = pc.svg.selectAll(".dimension");
	g.transition().duration(1100)
	    .attr("transform", function(p) { return "translate(" + position(p) + ")"; })
	    .style("opacity", 1);

	pc.svg.selectAll(".axis")
	    .transition()
	    .duration(1100)
	    .each(function(d) { d3.select(this).call(axis.scale(yscale[d])); });

	if (flags.shadows) paths(__.data, ctx.shadows);
	if (flags.brushable) pc.brushable();
	if (flags.reorderable) pc.reorderable();
	if (pc.brushMode() !== "None") {
	    var mode = pc.brushMode();
	    pc.brushMode("None");
	    pc.brushMode(mode);
	}
	return this;
    };

    // Jason Davies, http://bl.ocks.org/1341281
    pc.reorderable = function() {
	if (!g) pc.createAxes();

	// Keep track of the order of the axes to verify if the order has actually
	// changed after a drag ends. Changed order might have consequence (e.g.
	// strums that need to be reset).
	var dimsAtDragstart;

	g.style("cursor", "move")
	    .call(d3.behavior.drag()
		  .on("dragstart", function(d) {
		      dragging[d] = this.__origin__ = xscale(d);
		      dimsAtDragstart = __.dimensions.slice();
		  })
		  .on("drag", function(d) {
		      dragging[d] = Math.min(w(), Math.max(0, this.__origin__ += d3.event.dx));
		      __.dimensions.sort(function(a, b) { return position(a) - position(b); });
		      xscale.domain(__.dimensions);
		      pc.render();
		      g.attr("transform", function(d) { return "translate(" + position(d) + ")"; });
		  })
		  .on("dragend", function(d, i) {
		      // Let's see if the order has changed and send out an event if so.
		      var j = __.dimensions.indexOf(d),
			  parent = this.parentElement;

		      if (i !== j) {
			  events.axesreorder.call(pc, __.dimensions);
			  // We now also want to reorder the actual dom elements that represent
			  // the axes. That is, the g.dimension elements. If we don't do this,
			  // we get a weird and confusing transition when updateAxes is called.
			  // This is due to the fact that, initially the nth g.dimension element
			  // represents the nth axis. However, after a manual reordering,
			  // without reordering the dom elements, the nth dom elements no longer
			  // necessarily represents the nth axis.
			  //
			  // i is the original index of the dom element
			  // j is the new index of the dom element
			  parent.insertBefore(this, parent.children[j + 1])
		      }

		      delete this.__origin__;
		      delete dragging[d];
		      d3.select(this).transition().attr("transform", "translate(" + xscale(d) + ")");
		      pc.render();
		      if (flags.shadows) paths(__.data, ctx.shadows);
		  }));
	flags.reorderable = true;
	return this;
    };

    // pairs of adjacent dimensions
    pc.adjacent_pairs = function(arr) {
	var ret = [];
	for (var i = 0; i < arr.length-1; i++) {
	    ret.push([arr[i],arr[i+1]]);
	};
	return ret;
    };

    var brush = {
	modes: {
	    "None": {
		install: function(pc) {},           // Nothing to be done.
		uninstall: function(pc) {},         // Nothing to be done.
		selected: function() { return []; } // Nothing to return
	    }
	},
	mode: "None",
	predicate: "AND",
	currentMode: function() {
	    return this.modes[this.mode];
	}
    };

    // This function can be used for 'live' updates of brushes. That is, during the
    // specification of a brush, this method can be called to update the view.
    //
    // @param newSelection - The new set of data items that is currently contained
    //                       by the brushes
    function brushUpdated(newSelection) {
	__.brushed = newSelection;
	events.brush.call(pc,__.brushed);
	pc.render();
    }

    function brushPredicate(predicate) {
	if (!arguments.length) { return brush.predicate; }

	predicate = String(predicate).toUpperCase();
	if (predicate !== "AND" && predicate !== "OR") {
	    throw "Invalid predicate " + predicate;
	}

	brush.predicate = predicate;
	__.brushed = brush.currentMode().selected();
	pc.render();
	return pc;
    }

    pc.brushModes = function() {
	return Object.getOwnPropertyNames(brush.modes);
    };

    pc.brushMode = function(mode) {
	if (arguments.length === 0) {
	    return brush.mode;
	}

	if (pc.brushModes().indexOf(mode) === -1) {
	    throw "pc.brushmode: Unsupported brush mode: " + mode;
	}

	// Make sure that we don't trigger unnecessary events by checking if the mode
	// actually changes.
	if (mode !== brush.mode) {
	    // When changing brush modes, the first thing we need to do is clearing any
	    // brushes from the current mode, if any.
	    if (brush.mode !== "None") {
		pc.brushReset();
	    }

	    // Next, we need to 'uninstall' the current brushMode.
	    brush.modes[brush.mode].uninstall(pc);
	    // Finally, we can install the requested one.
	    brush.mode = mode;
	    brush.modes[brush.mode].install();
	    if (mode === "None") {
		delete pc.brushPredicate;
	    } else {
		pc.brushPredicate = brushPredicate;
	    }
	}

	return pc;
    };

    // brush mode: 1D-Axes

    (function() {
	var brushes = {};

	function is_brushed(p) {
	    return !brushes[p].empty();
	}

	// data within extents
	function selected() {
	    var actives = __.dimensions.filter(is_brushed),
		extents = actives.map(function(p) { return brushes[p].extent(); });

	    // We don't want to return the full data set when there are no axes brushed.
	    // Actually, when there are no axes brushed, by definition, no items are
	    // selected. So, let's avoid the filtering and just return false.
	    //if (actives.length === 0) return false;

	    // Resolves broken examples for now. They expect to get the full dataset back from empty brushes
	    if (actives.length === 0) return __.data;

	    // test if within range
	    var within = {
		/*
		"date-range": function(d,p,dimension) {
		    console.log("hello")
		    return extents[dimension][0] <= d[p] && d[p] <= extents[dimension][1]
		},
		*/
		"date": function(d,p,dimension) {
		    return extents[dimension][0] <= d[p] && d[p] <= extents[dimension][1]
		},
		"number": function(d,p,dimension) {

		    // console.log(d);

		    return extents[dimension][0] <= d[p] && d[p] <= extents[dimension][1]
		},

		// BL - added 'interval' type; this is crude
		"interval": function(d, p, dimension) {

		    // console.log("hello");

		    /*

		      var val = d[p];

		      var next_val = pc.toIntervalFloatArray(val);

		      var l = next_val[0];

		      var r = next_val[1];

		      var m = (l + r) / 2.0;

		    */
		    console.log(d[p], p)
		    var m = intervalStrToMidpoint([null, idempotentParsePossibleIntervalStrIntoMidpoint(d[p], pc, p), d[p], p], pc, false);

		    return extents[dimension][0] <= m && m <= extents[dimension][1];

		},

		"string": function(d,p,dimension) {
		    return extents[dimension][0] <= yscale[p](d[p]) && yscale[p](d[p]) <= extents[dimension][1]
		}
	    };

	    return __.data
		.filter(function(d) {
		    switch(brush.predicate) {
		    case "AND":
			return actives.every(function(p, dimension) {
			    return within[__.types[p]](d,p,dimension);
			});
		    case "OR":
			return actives.some(function(p, dimension) {
			    return within[__.types[p]](d,p,dimension);
			});
		    default:
			throw "Unknown brush predicate " + __.brushPredicate;
		    }
		});
	};

	function brushExtents() {
	    var extents = {};
	    __.dimensions.forEach(function(d) {
		var brush = brushes[d];
		// console.log(brush);
		if (!brush.empty()) {
		    var extent = brush.extent();
		    extent.sort(d3.ascending);
		    extents[d] = extent;
		}
	    });
	    return extents;
	}

	function brushFor(axis) {
	    var brush = d3.svg.brush();

	    brush
		.y(yscale[axis])
		.on("brushstart", function() { d3.event.sourceEvent.stopPropagation() })
		.on("brush", function() {
		    brushUpdated(selected());
		})
		.on("brushend", function() {
		    events.brushend.call(pc, __.brushed);
		});

	    brushes[axis] = brush;
	    return brush;
	}

	function brushReset(dimension) {
	    __.brushed = false;
	    if (g) {
		g.selectAll('.brush')
		    .each(function(d) {
			d3.select(this).call(
			    brushes[d].clear()
			);
		    });
		pc.render();
	    }
	    return this;
	};

	function install() {
	    if (!g) pc.createAxes();

	    // Add and store a brush for each axis.
	    g.append("svg:g")
		.attr("class", "brush")
		.each(function(d) {
		    d3.select(this).call(brushFor(d));
		})
		    .selectAll("rect")
		.style("visibility", null)
		.attr("x", -15)
		.attr("width", 30);

	    pc.brushExtents = brushExtents;
	    pc.brushReset = brushReset;
	    return pc;
	}

	brush.modes["1D-axes"] = {
	    install: install,
	    uninstall: function() {
		g.selectAll(".brush").remove();
		brushes = {};
		delete pc.brushExtents;
		delete pc.brushReset;
	    },
	    selected: selected
	}
    })();
    // brush mode: 2D-strums
    // bl.ocks.org/syntagmatic/5441022

    (function() {
	var strums = {},
	    strumRect;

	function drawStrum(strum, activePoint) {
	    var svg = pc.selection.select("svg").select("g#strums"),
		id = strum.dims.i,
		points = [strum.p1, strum.p2],
		line = svg.selectAll("line#strum-" + id).data([strum]),
		circles = svg.selectAll("circle#strum-" + id).data(points),
		drag = d3.behavior.drag();

	    line.enter()
		.append("line")
		.attr("id", "strum-" + id)
		.attr("class", "strum");

	    line
		.attr("x1", function(d) { return d.p1[0]; })
		.attr("y1", function(d) { return d.p1[1]; })
		.attr("x2", function(d) { return d.p2[0]; })
		.attr("y2", function(d) { return d.p2[1]; })
		.attr("stroke", "black")
		.attr("stroke-width", 2);

	    drag
		.on("drag", function(d, i) { 
		    var ev = d3.event;
		    i = i + 1;
		    strum["p" + i][0] = Math.min(Math.max(strum.minX + 1, ev.x), strum.maxX);
		    strum["p" + i][1] = Math.min(Math.max(strum.minY, ev.y), strum.maxY);
		    drawStrum(strum, i - 1);
		})
		.on("dragend", onDragEnd());

	    circles.enter()
		.append("circle")
		.attr("id", "strum-" + id)
		.attr("class", "strum");

	    circles
		.attr("cx", function(d) { return d[0]; })
	    // BL - thankfully, circles are not being used; d[1] can sometimes be not a number
		.attr("cy", function(d) { return d[1]; })
		.attr("r", 5)
		.style("opacity", function(d, i) {
		    return (activePoint !== undefined && i === activePoint) ? 0.8 : 0;
		})
		.on("mouseover", function() {
		    d3.select(this).style("opacity", 0.8);
		})
		.on("mouseout", function() {
		    d3.select(this).style("opacity", 0);
		})
		.call(drag);
	}

	function dimensionsForPoint(p) {
	    var dims = { i: -1, left: undefined, right: undefined };
	    __.dimensions.some(function(dim, i) {
		if (xscale(dim) < p[0]) {
		    var next = __.dimensions[i + 1];
		    dims.i = i;
		    dims.left = dim;
		    dims.right = next;
		    return false;
		}
		return true;
	    });

	    if (dims.left === undefined) {
		// Event on the left side of the first axis.
		dims.i = 0;
		dims.left = __.dimensions[0];
		dims.right = __.dimensions[1];
	    } else if (dims.right === undefined) {
		// Event on the right side of the last axis
		dims.i = __.dimensions.length - 1;
		dims.right = dims.left;
		dims.left = __.dimensions[__.dimensions.length - 2];
	    }

	    return dims;
	}

	function onDragStart() {
	    // First we need to determine between which two axes the sturm was started.
	    // This will determine the freedom of movement, because a strum can
	    // logically only happen between two axes, so no movement outside these axes
	    // should be allowed.
	    return function() {
		var p = d3.mouse(strumRect[0][0]),
		    dims = dimensionsForPoint(p),
		    strum = {
			p1: p,
			dims: dims,
			minX: xscale(dims.left),
			maxX: xscale(dims.right),
			minY: 0,
			maxY: h()
		    };

		strums[dims.i] = strum;
		strums.active = dims.i;

		// Make sure that the point is within the bounds
		strum.p1[0] = Math.min(Math.max(strum.minX, p[0]), strum.maxX);
		strum.p1[1] = p[1] - __.margin.top;
		strum.p2 = strum.p1.slice();
	    };
	}

	function onDrag() {
	    return function() {
		var ev = d3.event,
		    strum = strums[strums.active];

		// Make sure that the point is within the bounds
		strum.p2[0] = Math.min(Math.max(strum.minX + 1, ev.x), strum.maxX);
		strum.p2[1] = Math.min(Math.max(strum.minY, ev.y - __.margin.top), strum.maxY);
		drawStrum(strum, 1);
	    };
	}

	function containmentTest(strum, width) {
	    var p1 = [strum.p1[0] - strum.minX, strum.p1[1] - strum.minX],
		p2 = [strum.p2[0] - strum.minX, strum.p2[1] - strum.minX],
		m1 = 1 - width / p1[0],
		b1 = p1[1] * (1 - m1),
		m2 = 1 - width / p2[0],
		b2 = p2[1] * (1 - m2);

	    // test if point falls between lines
	    return function(p) {
		var x = p[0],
		    y = p[1],
		    y1 = m1 * x + b1,
		    y2 = m2 * x + b2;

		if (y > Math.min(y1, y2) && y < Math.max(y1, y2)) {
		    return true;
		}

		return false;
	    };
	}

	function selected() {
	    var ids = Object.getOwnPropertyNames(strums),
		brushed = __.data;

	    // Get the ids of the currently active strums.
	    ids = ids.filter(function(d) {
		return !isNaN(d);
	    });

	    function crossesStrum(d, id) {
		var strum = strums[id],
		    test = containmentTest(strum, strums.width(id)),
		    d1 = strum.dims.left,
		    d2 = strum.dims.right,
		    y1 = yscale[d1],
		    y2 = yscale[d2],
		    point = [y1(d[d1]) - strum.minX, y2(d[d2]) - strum.minX];
		return test(point);
	    }

	    if (ids.length === 0) { return brushed; }

	    return brushed.filter(function(d) {
		switch(brush.predicate) {
		case "AND":
		    return ids.every(function(id) { return crossesStrum(d, id); });
		case "OR":
		    return ids.some(function(id) { return crossesStrum(d, id); });
		default:
		    throw "Unknown brush predicate " + __.brushPredicate;
		}
	    });
	}

	function removeStrum() {
	    var strum = strums[strums.active],
		svg = pc.selection.select("svg").select("g#strums");

	    delete strums[strums.active];
	    strums.active = undefined;
	    svg.selectAll("line#strum-" + strum.dims.i).remove();
	    svg.selectAll("circle#strum-" + strum.dims.i).remove();
	}

	function onDragEnd() {
	    return function() {
		var brushed = __.data,
		    strum = strums[strums.active];

		// Okay, somewhat unexpected, but not totally unsurprising, a mousclick is
		// considered a drag without move. So we have to deal with that case
		if (strum && strum.p1[0] === strum.p2[0] && strum.p1[1] === strum.p2[1]) {
		    removeStrum(strums);
		}

		brushed = selected(strums);
		strums.active = undefined;
		__.brushed = brushed;
		pc.render();
		events.brushend.call(pc, __.brushed);
	    };
	}

	function brushReset(strums) {
	    return function() {
		var ids = Object.getOwnPropertyNames(strums).filter(function(d) {
		    return !isNaN(d);
		});

		ids.forEach(function(d) {
		    strums.active = d;
		    removeStrum(strums);
		});
		onDragEnd(strums)();
	    };
	}

	function install() {
	    var drag = d3.behavior.drag();

	    // Map of current strums. Strums are stored per segment of the PC. A segment,
	    // being the area between two axes. The left most area is indexed at 0.
	    strums.active = undefined;
	    // Returns the width of the PC segment where currently a strum is being
	    // placed. NOTE: even though they are evenly spaced in our current
	    // implementation, we keep for when non-even spaced segments are supported as
	    // well.
	    strums.width = function(id) {
		var strum = strums[id];

		if (strum === undefined) {
		    return undefined;
		}

		return strum.maxX - strum.minX;
	    };

	    pc.on("axesreorder.strums", function() {
		var ids = Object.getOwnPropertyNames(strums).filter(function(d) {
		    return !isNaN(d);
		});

		// Checks if the first dimension is directly left of the second dimension.
		function consecutive(first, second) {
		    var length = __.dimensions.length;
		    return __.dimensions.some(function(d, i) {
			return (d === first)
			    ? i + i < length && __.dimensions[i + 1] === second
			    : false;
		    });
		}

		if (ids.length > 0) { // We have some strums, which might need to be removed.
		    ids.forEach(function(d) {
			var dims = strums[d].dims;
			strums.active = d;
			// If the two dimensions of the current strum are not next to each other
			// any more, than we'll need to remove the strum. Otherwise we keep it.
			if (!consecutive(dims.left, dims.right)) {
			    removeStrum(strums);
			}
		    });
		    onDragEnd(strums)();
		}
	    });

	    // Add a new svg group in which we draw the strums.
	    pc.selection.select("svg").append("g")
		.attr("id", "strums")
		.attr("transform", "translate(" + __.margin.left + "," + __.margin.top + ")");

	    // Install the required brushReset function
	    pc.brushReset = brushReset(strums);

	    drag
		.on("dragstart", onDragStart(strums))
		.on("drag", onDrag(strums))
		.on("dragend", onDragEnd(strums));

	    // NOTE: The styling needs to be done here and not in the css. This is because
	    //       for 1D brushing, the canvas layers should not listen to
	    //       pointer-events.
	    strumRect = pc.selection.select("svg").insert("rect", "g#strums")
		.attr("id", "strum-events")
		.attr("x", __.margin.left)
		.attr("y", __.margin.top)
		.attr("width", w())
		.attr("height", h() + 2)
		.style("opacity", 0)
		.call(drag);
	}

	brush.modes["2D-strums"] = {
	    install: install,
	    uninstall: function() {
		pc.selection.select("svg").select("g#strums").remove();
		pc.selection.select("svg").select("rect#strum-events").remove();
		pc.on("axesreorder.strums", undefined);
		delete pc.brushReset;

		strumRect = undefined;
	    },
	    selected: selected
	};

    }());

    /*

    pc.setIsQuantFlags = function(condensed_column_is_quant_type_list) {
      this.condensed_column_is_quant_type_list = condensed_column_is_quant_type_list
      // console.log("hello")
      return this
    }

    */

    /*

    pc.setIsPercentFlags = function(condensed_column_is_percent_type_list) {
      this.condensed_column_is_percent_type_list = condensed_column_is_percent_type_list
      return this
    }

    */

    /*

    pc.setIsDateRangeFlags = function(condensed_column_is_date_range_type_list) {
      this.condensed_column_is_date_range_type_list = condensed_column_is_date_range_type_list
      return this
    }

    */

    /*

    pc.setColumnToColumnNumDict = function(column_name_to_column_num_dict) {
      this.column_name_to_column_num_dict = column_name_to_column_num_dict
      return this
    }

    */

    pc.interactive = function() {
	flags.interactive = true;
	return this;
    };

    // expose a few objects
    pc.xscale = xscale;
    pc.yscale = yscale;
    pc.ctx = ctx;
    pc.canvas = canvas;
    pc.g = function() { return g; };

    // rescale for height, width and margins
    // TODO currently assumes chart is brushable, and destroys old brushes
    pc.resize = function() {
	// selection size
	pc.selection.select("svg")
	    .attr("width", __.width)
	    .attr("height", __.height)
	pc.svg.attr("transform", "translate(" + __.margin.left + "," + __.margin.top + ")");

	// FIXME: the current brush state should pass through
	if (flags.brushable) pc.brushReset();

	// scales
	pc.autoscale();

	// axes, destroys old brushes.
	if (g) pc.createAxes();
	if (flags.shadows) paths(__.data, ctx.shadows);
	if (flags.brushable) pc.brushable();
	if (flags.reorderable) pc.reorderable();

	events.resize.call(this, {width: __.width, height: __.height, margin: __.margin});
	return this;
    };

    // highlight an array of data
    pc.highlight = function(data) {
	if (arguments.length === 0) {
	    return __.highlighted;
	}

	__.highlighted = data;
	pc.clear("highlight");
	d3.select(canvas.foreground).classed("faded", true);
	// console.log(data);
	data.forEach(path_highlight);
	events.highlight.call(this, data);
	// console.log("highlighted");
	return this;
    };

    // clear highlighting
    pc.unhighlight = function() {
	__.highlighted = [];
	pc.clear("highlight");
	d3.select(canvas.foreground).classed("faded", false);
	return this;
    };

    // calculate 2d intersection of line a->b with line c->d
    // points are objects with x and y properties
    pc.intersection =  function(a, b, c, d) {
	return {
	    x: ((a.x * b.y - a.y * b.x) * (c.x - d.x) - (a.x - b.x) * (c.x * d.y - c.y * d.x)) / ((a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x)),
	    y: ((a.x * b.y - a.y * b.x) * (c.y - d.y) - (a.y - b.y) * (c.x * d.y - c.y * d.x)) / ((a.x - b.x) * (c.y - d.y) - (a.y - b.y) * (c.x - d.x))
	};
    };

    function position(d) {
	var v = dragging[d];
	return v == null ? xscale(d) : v;
    }
    // BL - exposing position()
    pc.position = position
    pc.version = "0.5.0";
    // this descriptive text should live with other introspective methods
    pc.toString = function() { return "Parallel Coordinates: " + __.dimensions.length + " dimensions (" + d3.keys(__.data[0]).length + " total) , " + __.data.length + " rows"; };

    return pc;
};

d3.renderQueue = (function(func) {
    var _queue = [],                  // data to be rendered
	_rate = 10,                   // number of calls per frame
	_clear = function() {},       // clearing function
	_i = 0;                       // current iteration

    var rq = function(data) {
	if (data) rq.data(data);
	rq.invalidate();
	_clear();
	rq.render();
    };

    rq.render = function() {
	_i = 0;
	var valid = true;
	rq.invalidate = function() { valid = false; };

	function doFrame() {
	    if (!valid) return true;
	    if (_i > _queue.length) return true;

	    // Typical d3 behavior is to pass a data item *and* its index. As the
	    // render queue splits the original data set, we'll have to be slightly
	    // more carefull about passing the correct index with the data item.
	    var end = Math.min(_i + _rate, _queue.length);
	    for (var i = _i; i < end; i++) {
		func(_queue[i], i);
	    }
	    _i += _rate;
	}

	d3.timer(doFrame);
    };

    rq.data = function(data) {
	rq.invalidate();
	_queue = data.slice(0);
	return rq;
    };

    rq.rate = function(value) {
	if (!arguments.length) return _rate;
	_rate = value;
	return rq;
    };

    rq.remaining = function() {
	return _queue.length - _i;
    };

    // clear the canvas
    rq.clear = function(func) {
	if (!arguments.length) {
	    _clear();
	    return rq;
	}
	_clear = func;
	return rq;
    };

    rq.invalidate = function() {};

    return rq;
});
