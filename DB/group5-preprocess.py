import pandas as pd

# CUSTOMER
# Latitude, Longitude drop outliers
df = pd.read_csv('train_locations.csv')

df = df[(df['latitude'] > -5) & (df['latitude'] < 5) & (df['longitude'] > -5) & (df['longitude'] < 5)]
df['location_number'] = df.groupby('customer_id').cumcount()
#df.to_csv('customer.csv', index=False) # this is preprocessed dataset

# VENDOR_TAG
# create tag numbers and tags
# https://www.kaggle.com/datasets/mrmorj/restaurant-recommendation-challenge/data 
vendor = pd.read_csv("vendors_original.csv") # this is original dataset from kaggle
vendor = vendor[['vendor_tag','vendor_tag_name']]
tag_dict = {}

for idx, row in vendor.iterrows():
    if pd.notnull(row['vendor_tag']) and pd.notnull(row['vendor_tag_name']):
        tags = row['vendor_tag'].split(',')
        tag_names = row['vendor_tag_name'].split(',')

        for tag, tag_name in zip(tags, tag_names):
            if tag not in tag_dict:
                tag_dict[tag] = tag_name

vendor_tag = pd.DataFrame(list(tag_dict.items()), columns=['vendor_tag', 'vendor_tag_name'])
vendor_tag['vendor_tag'] = vendor_tag['vendor_tag'].astype(int)
vendor_tag.sort_values(by=['vendor_tag'], inplace = True)
#vendor_tag.to_csv('vendor_tag.csv', index=False) # this is preprocessed dataset


# VENDOR_CATEGORY
category_mapping = {
    'Cuisine': ['American', 'Arabic', 'Asian', 'Chinese', 'Indian', 'Japanese', 'Lebanese', 'Omani', 'Thai', 'Italian', 'Mexican'],
    'Fast Food': ['Burgers', 'Sandwiches', 'Pizzas', 'Hot Dogs', 'Fries'],
    'Healthy Options': ['Healthy Food', 'Salads', 'Vegetarian', 'Organic'],
    'Desserts & Sweets': ['Desserts', 'Cakes', 'Ice creams', 'Sweets', 'Donuts', 'Churros', 'Frozen yoghurt'],
    'Beverages': ['Milkshakes', 'Smoothies', 'Fresh Juices', 'Coffee', 'Hot Chocolate', 'Mojitos', 'Karak', 'Spanish Latte'],
    'Snacks & Sides': ['Waffles', 'Bagels', 'Rolls', 'Fatayers', 'Pancakes', 'Pastry', 'Dimsum'],
    'Grilled & BBQ': ['Grills', 'Shawarma', 'Kebabs', 'Steaks'],
    'Seafood & Meat': ['Seafood', 'Biryani', 'Sushi'],
    'Bakery & Dough': ['Cafe', 'Pasta', 'Soups', 'Crepes', 'Manakeesh', 'Pizza', 'Pastas']
}

flattened_categories = [(major, sub) for major, subs in category_mapping.items() for sub in subs]

vendor_category = pd.DataFrame(columns=['Major Category', 'Sub Category', 'vendor_tag_num'])

for major, sub in flattened_categories:
    tag_nums = vendor_tag.loc[vendor_tag['vendor_tag_name'].str.lower() == sub.lower(), 'vendor_tag']
    if not tag_nums.empty:
        vendor_category = vendor_category.append({
            'Major Category': major,
            'Sub Category': sub,
            'vendor_tag_num': tag_nums.iloc[0]
        }, ignore_index=True)
vendor_category
#vendor_category.to_csv('vendor_category.csv', index=False) # this is preprocessed dataset

# LIKES
# https://www.kaggle.com/datasets/mrmorj/restaurant-recommendation-challenge/data 
orders = pd.read_csv("orders.csv") # this is original dataset from kaggle
rating = orders[['customer_id','vendor_id','is_rated','vendor_rating']]
# dropping null values
available_rating = rating.dropna(axis=0)
available_rating = available_rating[available_rating['is_rated']=='Yes']
# get records of rating 5 and eliminate if there are duplicated values
like_table = available_rating[available_rating['vendor_rating']==5][['customer_id','vendor_id','vendor_rating']].drop_duplicates()
like_table = like_table[['customer_id','vendor_id']]
like_table['like'] = 1
#like_table.to_csv("likes.csv",index=False) # this is preprocessed dataset

# VENDORS
# https://www.kaggle.com/datasets/mrmorj/restaurant-recommendation-challenge/data 
vendor = pd.read_csv("vendors_original.csv") # this is original dataset from kaggle
vendor = vendor[['id','latitude','longitude','delivery_charge','OpeningTime','is_open','prepration_time','discount_percentage','vendor_rating']]

# renaming columns
vendor.rename(columns={"id":"vendor_id"},inplace=True)
vendor.rename(columns={"prepration_time":"preparation_time"},inplace=True)

# separating OpeningTime to open_time and end_time
start_end_time = {"open_time":[],"end_time":[]}
error_index = []
for i,ot in enumerate(vendor['OpeningTime']):
    try:
        start = pd.to_datetime(ot.split('-')[0]).strftime('%H:%M')
        end = pd.to_datetime(ot.split('-')[1]).strftime('%H:%M')
    except AttributeError:
        start = None
        end = None
    except:
        start = ot.split('-')[0]
        end = ot.split('-')[1]
        error_index.append(i)

    start_end_time["open_time"].append(start)
    start_end_time["end_time"].append(end)
start_end_time = pd.DataFrame.from_dict(start_end_time)

# change which have values, but is not correctly converted
start_end_time.iloc[35] = (pd.to_datetime("11:30AM").strftime('%H:%M'),pd.to_datetime("11:30PM").strftime('%H:%M'))
start_end_time.iloc[55] = (pd.to_datetime("09:00AM").strftime('%H:%M'),pd.to_datetime("10:00PM").strftime('%H:%M'))
start_end_time.iloc[57] = (pd.to_datetime("01:00PM").strftime('%H:%M'),pd.to_datetime("02:00AM").strftime('%H:%M'))
start_end_time.iloc[62] = (pd.to_datetime("11:00AM").strftime('%H:%M'),pd.to_datetime("11:00PM").strftime('%H:%M'))
start_end_time.iloc[64] = (pd.to_datetime("11:30AM").strftime('%H:%M'),pd.to_datetime("11:59PM").strftime('%H:%M'))
start_end_time.iloc[73] = (pd.to_datetime("11:00AM").strftime('%H:%M'),pd.to_datetime("11:00PM").strftime('%H:%M'))
start_end_time.iloc[88] = (pd.to_datetime("09:00AM").strftime('%H:%M'),pd.to_datetime("10:00PM").strftime('%H:%M'))
start_end_time.iloc[90] = (pd.to_datetime("09:00AM").strftime('%H:%M'),pd.to_datetime("10:00PM").strftime('%H:%M'))

# replace 'OpeningTime' to 'open_time' and 'end_time'
vendor.insert(5, "open_time", start_end_time["open_time"])
vendor.insert(6, "end_time", start_end_time["end_time"])
vendor.drop(columns="OpeningTime",inplace=True)

# make 'is_open' datatype integer for database
vendor['is_open'] = vendor['is_open'].apply(int)
#vendor.to_csv('vendors.csv', index=False) # this is preprocessed dataset