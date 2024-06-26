import mysql.connector
from tkinter import *
import tkinter.messagebox as msgbox
from tkinter import _setit
from tkinter import END
import math
from mysql.connector import Error
from tkinter import ttk 
from tkintermapview import TkinterMapView

db_config = {
    'host': 'localhost',
    'database': 'project',
    'user': 'root',
    'password': '' # insert user password
}

def connectDB(db_use):
    mydb = mysql.connector.connect(
    host="localhost",
    user = "root",
    passwd = "", # insert user password
    database = db_use
)
    mycursor = mydb.cursor()
    return mydb, mycursor

mydb, myCursor = connectDB("project")

#### GUI ####
# GUI
# id example:
# IL9MJSW
# 00OT8JX
# 30PZXDS

# Login function
def login():
    global customer_id
    customer_id = id_entry.get()
    myCursor.execute("SELECT location_number, latitude, longitude FROM customer WHERE customer_id = %s", (customer_id,))
    result = myCursor.fetchall()

    if result:
        msgbox.showinfo("Login success", "You are successfully logged in.")
        init_map() # Initialize the map
        show_location_nums(result) # Display list of location numbers
        show_locations_on_map(result) # Display locations on the map
    else:
        msgbox.showerror("Login failed", "The user name entered is incorrect.\nPlease try again.")

# Map intializtion
def init_map():
    global gmap_widget
    gmap_widget = TkinterMapView(window, width=500, height=400)
    gmap_widget.pack(fill='both', expand = True, side='right')

# Function to display location numbers in the GUI
def show_location_nums(locations):
		# Clear existing widgets in the location frame
    for widget in location_frame.winfo_children():
        widget.destroy()

		# Create and pack radio buttons for each location
    for location in locations:
        location_num = location[0]
        radio_button = Radiobutton(location_frame, text=str(location_num), variable=location_var, value=location_num)
        radio_button.pack(side='left', padx=20)

# Function to display locations on the map
def show_locations_on_map(locations):
		# Add markers for each location
    for location in locations:
        location_num, lat, lon = location
        if lat and lon:
            lat = float(lat)
            lon = float(lon)
            point = gmap_widget.set_position(lat, lon, marker=True)
            point.set_text(f"Location {location_num}")

    # Set zoom level
    gmap_widget.set_zoom(5)

# Function to fetch a customer's location data
def fetch_customer_location(customer_id, location_num):
    # 사용자가 찍은 위치 가져오기
    query = "SELECT latitude, longitude FROM customer WHERE customer_id = %s AND location_number = %s" 
    myCursor.execute(query, (customer_id, location_num))
    result = myCursor.fetchone()
    return result if result else (None, None)

# Function to fetch vendor locations based on a subcategory
def fetch_vendors_location(sub_category_num):
    # get vendors that match a specific subcategory
    query = "SELECT id, latitude, longitude FROM vendor_tag vt JOIN vendors v ON vt.id=v.vendor_id WHERE vendor_tag = %s"
    myCursor.execute(query, (sub_category_num,))
    return myCursor.fetchall()

# Function to calculate distance between two points
def distance_cal(lat1, lon1, lat2, lon2):
    # Euclidean distance calculation
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

# Function to fetch vendors based on customer location and subcategory
def fetch_vendors(customer_id, location_num, sub_category_num):
    # Retrieve customer's location
    customer_lat, customer_lon = fetch_customer_location(customer_id, location_num)
		# Retrieve vendor locations matching the subcategory
    vendors = fetch_vendors_location(sub_category_num)

    # Return blank list if customer location information is not available
    if customer_lat is None or customer_lon is None:
        return [] 

    vendors_with_distance = []
		# Calculate and store distances from each vendor to the customer
    for vendor_id, vendor_lat, vendor_lon in vendors:
        distance = distance_cal(customer_lat, customer_lon, vendor_lat, vendor_lon) # Calculate the distance between each restaurant and its users
        # For each restaurant, distance information between the user and the restaurant is stored in the form of a tuple
        vendors_with_distance.append((vendor_id, distance))

    # Sort by distance (vendor_id, distance)
    vendors_with_distance.sort(key=lambda x: x[1])

    # Create a list to put queries in the nearest order
    vendors_info = []
    for vendor_id, _ in vendors_with_distance:
        myCursor.execute("""
            SELECT vendor_id, vendor_rating, delivery_charge, preparation_time, open_time,end_time,is_open,sum(`like`)
            FROM vendors JOIN likes USING (vendor_id)
            GROUP BY vendor_id
            HAVING vendor_id = %s
        """, (vendor_id,))
        vendor_data = myCursor.fetchone()
        if vendor_data:
            vendors_info.append(vendor_data)
    return vendors_info # List of queries sorted by distance 

# Functions received as querying restaurant information on sale
def fetch_discounted_vendors():
    try:  # When you connect to the database
        connection = mysql.connector.connect(**db_config) # Connect DB with db_config
        if connection.is_connected(): # When it's connected
            cursor = connection.cursor() 
            query = "SELECT vendor_id, discount_percentage, vendor_rating, delivery_charge, preparation_time, open_time,end_time,is_open,sum(`like`) FROM vendors JOIN likes USING (vendor_id) GROUP BY vendor_id having discount_percentage > 0"  # 할인률 0초과인거만 조회
            cursor.execute(query)
            result = cursor.fetchall() 
            return result 

    except Error as e:
        msgbox.showerror("Database Connection Error", str(e)) 
    finally: 
        if connection.is_connected():
            cursor.close()
            connection.close()

# Sorting by different criteria
def fetch_vendors_orderby(vendor_ids, sort_by):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            ####################################################
            vendor_ids_sql = tuple([v[0] for v in vendor_ids])
            #print("vendor_ids_sql:",vendor_ids_sql)
            query = f"SELECT vendor_id, vendor_rating, delivery_charge, preparation_time, open_time,end_time,is_open,sum(`like`) FROM vendors JOIN likes USING (vendor_id) GROUP BY vendor_id HAVING vendor_id IN {vendor_ids_sql}"
            ####################################################
            if sort_by == 'delivery':  # Sort by delivery charge
                query += " ORDER BY delivery_charge;"
            elif sort_by == 'preparation': # Sort by food preparation time 
                query += " ORDER BY preparation_time;"
            elif sort_by == 'rating':  # Sort by rating
                query += " ORDER BY vendor_rating DESC;"
            elif sort_by == 'open':   # Restaurant open by user's connected time  
                query += " AND HOUR(CURTIME()) BETWEEN HOUR(open_time) AND HOUR(end_time) ORDER BY vendor_id;"
            
            cursor.execute(query)
            #print("this is okay")
            result = cursor.fetchall()
            return result # This is also received in the form of a result for a query
    except Error as e:
        print("Database Connection Error", str(e))
        return []  # Return blank list in case of exception
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
def refresh_list(sort_by,vendor_frame,status_label,scrollcanvas): # A function that rearranges when the sort button is pressed
    # The location number selected on the radio button
    location_num = location_var.get() 
    # Get the name of the selected subcategory from OptionMenu
    sub_category_name = sub_category_var.get()  
    # Convert tag name to tag number
    sub_category_num = fetch_vendor_tag_num(sub_category_name)
    # Get all search results with tag number
    vendor_ids = fetch_vendors(customer_id, location_num, sub_category_num)

    # If there is no restaurant in the received result, treat it as a blank list
    if vendor_ids is None:
        vendor_ids = []
        status_label.config(text="there is no vendor you are searching") 

    # Sorting the restaurants received
    vendors = fetch_vendors_orderby(vendor_ids, sort_by)

    if vendors is None:
        vendors = []  # If the vendor is None, treat it as an empty list
        status_label.config(text="there is no vendor you are searching")
    
    # initialize the frame's grid
    for widget in vendor_frame.winfo_children():
        widget.destroy()  

    if not vendors:
        status_label.config(text="there is no vendor you are searching")

    else:
        status_label.config(text="")
				# insert columns to table
        for i, value in enumerate(['vendor ID','rating','delivery charge','preparation time','details','like','total likes']):
            Label(vendor_frame, text=value, bg="grey",borderwidth=2, padx=10, pady=2).grid(row=1, column=i)
        # Insert results into the grid
        for i, result in enumerate(vendors):
            for j, value in enumerate(result[:4]):
                Label(vendor_frame, text=value, bg="white",borderwidth=2, padx=10, pady=2).grid(row=i+2, column=j)
            btn_show_details = Button(vendor_frame, text="Show Details", command=lambda row=i, values=result: show_details_popup(values))
            btn_show_details.grid(row=i+2, column=j+1)
            like_dic = get_likes(customer_id)
            try:
                if like_dic[result[0]]:
                    t = "♥"
                else:
                    t = '♡'
            except:
                t = '♡'

            btn_like = Button(vendor_frame, text=t,padx=20)
            btn_like.config(command=lambda row=i, values=result, btn=btn_like: update_like_main(values,customer_id,btn))
            btn_like.grid(row=i+2, column=j+2)
            Label(vendor_frame, text=result[7], bg="white",borderwidth=2, padx=10, pady=2).grid(row=i+2, column=j+3)
            
    scrollcanvas.update_idletasks()
    scrollcanvas.config(scrollregion=scrollcanvas.bbox('all')) 

# Category Selection Screen
def open_category_selection_window():
    category_window = Toplevel(window)
    category_window.title("Vendor Categories")
    category_window.geometry("800x800")

    global major_category_var
    global sub_category_var
    global like_dic
    
    major_category_var = StringVar() # Variables that will contain the selected major classification of strings
    sub_category_var = StringVar() # Variables that will contain a string of selected subcategories

    # the phrase that comes up at the top
    label = Label(category_window, text = 'Vendors For You',font = ('Arial',18))
    label.place(relx=0.1,rely=0,relwidth=0.8,relheight=0.1)

    button = Button(category_window, text="View likes", command=lambda:on_button_click(category_window))
    button.place(relx=0.8,rely=0.03)

    # Frame to put the Select Classification button
    category_frame = Frame(category_window, bg = '#80c1ff')
    category_frame.place(relx=0.1,rely=0.1,relwidth=0.8,relheight=0.05)

    # Major category menu labels
    Label(category_frame, text="Major Category").place(relx= 0.05, rely = 0.1, relwidth = 0.25, relheight= 0.8)
    myCursor.execute("SELECT DISTINCT Major_category FROM category")
    major_categories = [item[0] for item in myCursor.fetchall()]

    # Select major category toggle
    main_category_menu = OptionMenu(category_frame, major_category_var, *major_categories)
    main_category_menu.place(relx=0.3, rely=0.1, relwidth=0.15, relheight=0.8)

    # Sub-category menu labels
    Label(category_frame, text="Sub Category").place(relx= 0.55, rely = 0.1, relwidth = 0.25, relheight= 0.8)
    
		# Select subcategory toggle
    sub_category_menu = OptionMenu(category_frame, sub_category_var, "Select a sub category")
    sub_category_menu.place(relx=0.8, rely=0.1, relwidth=0.15, relheight=0.8)

    # a frame showing a discounted restaurant
    discounted_frame = Frame(category_window)
    discounted_frame.place(relx = 0,rely=0.15,relwidth=1,relheight=0.215)
		
    discounted_label = Label(discounted_frame, text="Discounted Restaurants")
    discounted_label.place(relx = 0.1, rely=0,relwidth=0.8,relheight=0.1)
		
		# LabelFrame for table
    discounted_list = LabelFrame(discounted_frame,bg='white')
    discounted_list.place(relx=0.1, rely=0.12,relwidth=0.8,relheight=0.88)

		# insert columns to table
    for i, value in enumerate(['vendor ID','discount %','rating','delivery charge','preparation time','details','like','total likes']):
            Label(discounted_list, text=value, bg="grey",borderwidth=2, padx=10, pady=2).grid(row=1, column=i)
    
		# Insert results into the grid
    for i, result in enumerate(fetch_discounted_vendors()):
        for j, value in enumerate(result[:5]):
            Label(discounted_list, text=value, bg="white",borderwidth=2, padx=10, pady=2).grid(row=i+2, column=j)
        btn_show_details = Button(discounted_list, text="Show Details", command=lambda row=i, values=result: show_details_popup(values))
        btn_show_details.grid(row=i+2, column=j+1)
        like_dic = get_likes(customer_id)
        try:
            if like_dic[result[0]]:
                t = "♥"
            else:
                t = '♡'
        except:
            t = '♡'

        btn_like = Button(discounted_list, text=t,padx=20)
        btn_like.config(command=lambda row=i, values=result, btn=btn_like: update_like_main(values,customer_id,btn))
        btn_like.grid(row=i+2, column=j+2)
        Label(discounted_list, text=result[8], bg="white",borderwidth=2, padx=10, pady=2).grid(row=i+2, column=j+3)

    for i in range(6):  # Suppose there are six rows
        discounted_list.columnconfigure(i, weight=1)

    # Sort button -> Press to change list box
    sort_rating_button = Button(category_window, text="Rating",command=lambda: refresh_list('rating',vendor_frame,vstatus_label,gridboxcanvas))
    sort_delivery_button = Button(category_window, text="Delivery Charge",command=lambda: refresh_list('delivery',vendor_frame,vstatus_label,gridboxcanvas))
    sort_cooking_button = Button(category_window, text="Preparation Time",command=lambda: refresh_list('preparation',vendor_frame,vstatus_label,gridboxcanvas))
    sort_distance_button = Button(category_window, text="Open",command=lambda: refresh_list('open',vendor_frame,vstatus_label,gridboxcanvas))

    sort_rating_button.place(relx=0.1,rely = 0.375, relwidth=0.17, relheight=0.04)
    sort_delivery_button.place(relx=0.31, rely=0.375,relwidth=0.17,relheight=0.04)
    sort_cooking_button.place(relx=0.52, rely=0.375,relwidth=0.17,relheight=0.04)
    sort_distance_button.place(relx=0.73, rely=0.375,relwidth=0.17,relheight=0.04)
		
		# LabelFrame for table
    vendors_gridbox = LabelFrame(category_window, bg="white")
    vendors_gridbox.place(relx=0.1,rely=0.425,relwidth=0.8,relheight=0.55)
    
		# canvas for table
    gridboxcanvas = Canvas(vendors_gridbox, bg='white')
    gridboxcanvas.pack(side=LEFT,fill="both",expand="yes")

		# label for showing result status
    vstatus_label = Label(vendors_gridbox, bg="white")
    vstatus_label.place(relx=0.5, rely=0.5, anchor="center")
		
		# insert Scrollbar
    boxyscrollbar = ttk.Scrollbar(vendors_gridbox, orient="vertical", command=gridboxcanvas.yview)
    boxyscrollbar.pack(side=RIGHT, fill="y")
    gridboxcanvas.configure(yscrollcommand=boxyscrollbar.set)
    gridboxcanvas.bind('<Configure>',lambda e:gridboxcanvas.configure(scrollregion=gridboxcanvas.bbox('all')))
		
		# scrollable frame
    vendor_frame = Frame(gridboxcanvas, bg="white")
    gridboxcanvas.create_window((0,0),window=vendor_frame, anchor="n")
    gridboxcanvas.pack(fill="both", expand="yes", padx=25, pady=10)
		
		# selecting category and show result
    major_category_var.trace('w', lambda *args: on_main_category_change(*args, major_category_var=major_category_var, sub_category_var=sub_category_var, sub_category_menu=sub_category_menu))
    sub_category_var.trace('w', lambda *args: on_sub_category_change(*args, sub_category_var=sub_category_var, vendor_frame=vendor_frame,scrollcanvas=gridboxcanvas,status_label=vstatus_label)) # vendors_listbox대신 프레임을 입력 받게 하자

# popup screen for view like button
def view_like_window(user,win):
    # popup screen to display liked vendors
    like_popup = Toplevel(win)
    like_popup.title("View likes")
    like_popup.geometry("510x500")

    # top_frame
    top_frame = Frame(like_popup,bg='white')
    top_frame.place(relheight=0.2, relwidth=1)
    top_label = Label(top_frame, text="view likes", font=("Arial", 20),bg='white')
    top_label.place(relx=0.5, rely=0.5, anchor="center")
    column_frame = Frame(like_popup, bg="white")
    column_frame.place(relheight=0.05, relwidth=1, rely=0.2)

    # frame for table
    table_frame = Frame(like_popup, bg="white")
    table_frame.place(relheight=0.75, relwidth=1, rely=0.25)
    status_label = Label(table_frame, bg="white")
    status_label.place(relx=0.5, rely=0.5, anchor="center")

    # canvas for table
    mycanvas = Canvas(table_frame,bg="white")
    mycanvas.pack(side=LEFT,fill="both",expand="yes")

    # insert Scrollbar
    yscrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=mycanvas.yview)
    yscrollbar.pack(side=RIGHT, fill="y")
    mycanvas.configure(yscrollcommand=yscrollbar.set)
    mycanvas.bind('<Configure>',lambda e:mycanvas.configure(scrollregion=mycanvas.bbox('all')))

    # scrollable frame
    myframe = Frame(mycanvas, bg="white")
    mycanvas.create_window((0,0),window=myframe)
    mycanvas.pack(fill="both")

    # Query the database to retrieve the list of vendors liked by the customer_id
    mydb, myCursor = connectDB("project")
    query = f"SELECT vendor_id, vendor_rating, delivery_charge, preparation_time, open_time,end_time,is_open,`like` FROM vendors v JOIN likes USING (vendor_id) WHERE customer_id = '{user}' && `like` = 1"
    myCursor.execute(query)
    results = myCursor.fetchall()
    mydb.close()

    if not results:
        status_label.config(text="there is no liked vendor")
    else:
        status_label.config(text="")
				# insert column
        for i, value in enumerate(['vendor ID','rating','delivery charge','preparation time','details','like']):
            Label(myframe, text=value, bg="grey",borderwidth=2, padx=10, pady=2).grid(row=1, column=i)
        # insert results into the grid
        for i, result in enumerate(results):
            for j, value in enumerate(result[:4]):
                Label(myframe, text=value, bg="white",borderwidth=2, padx=10, pady=2).grid(row=i+2, column=j)
            btn_show_details = Button(myframe, text="Show Details", command=lambda row=i, values=result: show_details_popup(values))
            btn_show_details.grid(row=i+2, column=j+1)
            btn_like = Button(myframe, text="♥",padx=20)
            btn_like.config(command=lambda row=i, values=result, btn=btn_like: update_like_main(values,user,btn))
            btn_like.grid(row=i+2, column=j+2)

# function for clicking 'view like' button
def on_button_click(win):
    view_like_window(customer_id,win)

# Restaurant lookup window turned on when location is selected
def on_confirm():
    selected_location_num = location_var.get()
    open_category_selection_window()

# category
def fetch_sub_categories(Major_category):
    ''' Import subcategories corresponding to the major categories you clicked '''
    query = "SELECT Sub_category FROM category WHERE Major_category = %s"
    myCursor.execute(query, (Major_category,))
    return [item[0] for item in myCursor.fetchall()]


def on_main_category_change(*args, major_category_var, sub_category_var, sub_category_menu):
    '''Call when major category changes'''
    major_category = major_category_var.get() # Import major category names
    sub_categories = fetch_sub_categories(major_category) # Import subcategories of major categories
    #print("sub_category_menu['menu']:",sub_category_menu['menu'])
    sub_category_menu['menu'].delete(0, 'end') # Initialize items that were in the previous subcategory list (clear what was written before the major category selection)

    for sub_category in sub_categories: # Add the sub-classification names received as sub-classification options
        sub_category_menu['menu'].add_command(label=sub_category, command=lambda value=sub_category: sub_category_var.set(value))


def fetch_vendor_tag_num(sub_category_name):
    """Get vendor_tag_num corresponding to the given subcategory name"""
    query = "SELECT vendor_tag_num FROM category WHERE Sub_category = %s"
    myCursor.execute(query, (sub_category_name,))
    result = myCursor.fetchone()
    return result[0] if result else None

def on_sub_category_change(*args,sub_category_var, vendor_frame, scrollcanvas,status_label):
    global customer_id
    sub_category_name = sub_category_var.get() # Get the name of the item selected in the subcategory
    sub_category_num = fetch_vendor_tag_num(sub_category_name) # Get the tag number of the selected item name

    selected_location_num = location_var.get() # Get user location number
    vendors = fetch_vendors(customer_id, selected_location_num, sub_category_num) # Obtain a user location for that category
    print("Fetched vendors:", vendors) 
    print(customer_id)
    print(selected_location_num)
		
		# reset the frame's whole grid
    for widget in vendor_frame.winfo_children():
        widget.destroy()
		
    if not vendors:
        status_label.config(text="there is no vendor you are searching")

    else:
        status_label.config(text="")
				# insert columns into the grid
        for i, value in enumerate(['vendor ID','rating','delivery charge','preparation time','details','like','total likes']):
            Label(vendor_frame, text=value, bg="grey",borderwidth=2, padx=10, pady=2).grid(row=1, column=i)
        # insert results into the grid
        for i, result in enumerate(vendors):
            for j, value in enumerate(result[:4]):
                Label(vendor_frame, text=value, bg="white",borderwidth=2, padx=10, pady=2).grid(row=i+2, column=j)
            btn_show_details = Button(vendor_frame, text="Show Details", command=lambda row=i, values=result: show_details_popup(values))
            btn_show_details.grid(row=i+2, column=j+1)
            like_dic = get_likes(customer_id)
            try:
                if like_dic[result[0]]:
                    t = "♥"
                else:
                    t = '♡'
            except:
                t = '♡'

            btn_like = Button(vendor_frame, text=t,padx=20)
            btn_like.config(command=lambda row=i, values=result, btn=btn_like: update_like_main(values,customer_id,btn))
            btn_like.grid(row=i+2, column=j+2)
            Label(vendor_frame, text=result[7], bg="white",borderwidth=2, padx=10, pady=2).grid(row=i+2, column=j+3)
    
		# make scrollbar adapt to updated vendors list        
    scrollcanvas.update_idletasks()
    scrollcanvas.config(scrollregion=scrollcanvas.bbox('all'))

# function for 'show details' button
def show_details_popup(values):
        
        popup = Toplevel()
        popup.title("Details")

        column_names = ['vendor ID', 'rating', 'delivery charge', 'preparation time', 'open time', 'close time', 'is open']

        for col_name, value in zip(column_names, values):
            # Display "yes" for is_open when it's 1, and "no" when it's 0
            if col_name == 'is open':
                value = 'yes' if value == 1 else 'no'
            Label(popup, text=f"{col_name}: {value}", anchor="w").pack()  

# function for making 'like' history
def get_likes(customer_id):
    mydb, myCursor = connectDB("project")
    query = f"SELECT * FROM likes WHERE customer_id='{customer_id}'"
    myCursor.execute(query)
    results = myCursor.fetchall()
    like_dic = dict()
		# make dictionary containing vendors' status 1(like)/0(normal)
		# the dictionary is used to get information if the customer have ever pressed "like" before
		# only if the ID exists as a key value is important
    for r in results:
        like_dic[r[1]] = r[2]
    return like_dic

# function for updating 'like' status
def update_like_main(values,user,btn):
    vendor_id = values[0]
		# if a vendor's status is 'like', the status is switched to 'normal'
    if btn.cget('text') == '♥': 
        update_query = f"UPDATE likes SET `like` = 0 WHERE vendor_id = {vendor_id} && customer_id = '{user}'"
        myCursor.execute(update_query)
        mydb.commit()
        btn['text'] = '♡'
		# if a vendor's status is 'normal', the status is switched to 'like'
    else:
        try: # Use "UPDATE" if the customer have ever pressed "like" before
            like_dic[vendor_id] 
            update_query = f"UPDATE likes SET `like` = 1 WHERE vendor_id = {vendor_id} && customer_id = '{user}'"
        except: # Use "INSERT" if the customer have never pressed "like" before
            update_query = f"INSERT INTO likes VALUES ('{user}',{vendor_id},1)"
            like_dic[vendor_id] = 1
        myCursor.execute(update_query)
        mydb.commit()
        btn['text'] = '♥'

# main
window = Tk()
window.title("Log In")
window.geometry("600x500")

center_frame = Frame(window)
center_frame.pack(pady=100)

Label(center_frame, text="USER ID:").pack()
id_entry = Entry(center_frame)
id_entry.pack()

login_button = Button(center_frame, text="Log In", command=login)
login_button.pack(pady=10)

location_frame = Frame(center_frame)
location_frame.pack()

location_var = StringVar()
location_var.set(" ")

confirm_button = Button(center_frame, text="Confirm", command=on_confirm)
confirm_button.pack(pady=10)

window.mainloop()