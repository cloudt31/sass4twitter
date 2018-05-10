from shapely.geometry import Point


def find_bounding_box_area(city_polygon_dictionary, city_line_dictionary, list_of_coordinates):
    longitude = (list_of_coordinates[0][0][0] + list_of_coordinates[0][2][0]) / 2
    latitude = (list_of_coordinates[0][0][1] + list_of_coordinates[0][1][1]) / 2
    coordinate = Point(longitude, latitude)
    return find_point_area(city_polygon_dictionary, city_line_dictionary, coordinate)


def find_point_area(city_polygon_dictionary, city_line_dictionary, point_coordinates):
    area_code = None
    list_deet = [None, None]
    for key in city_polygon_dictionary.keys():
        # print((polygon_dictionary[key]))
        for sub_key in city_polygon_dictionary[key]:
            if city_polygon_dictionary[key][sub_key].intersects(point_coordinates) or city_line_dictionary[key][
                sub_key].intersects(point_coordinates) or point_coordinates.touches(
                city_polygon_dictionary[key][sub_key]):
                area_code = key
                # print(key)
                break
            else:
                pass
    if area_code is not None:
        list_deet = []
        list_deet = area_code.split(',')
    return list_deet
