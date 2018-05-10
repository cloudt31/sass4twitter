def immigrant_percentage(area_csv):
    with open(area_csv, 'r') as f:
        immigrant_details = []
        for i in f:
            listing = i.split(',')
            if i.startswith('sa3'):
                pass
            else:
                temp_list = [listing[3].strip('"\n'), (((int(listing[1]) - int(listing[2])) / int(listing[1])) * 100)]
                immigrant_details.append(temp_list)
    return immigrant_details


if __name__ == '__main__':
    print(immigrant_percentage('Perth_CountryOfBirth.csv'))
