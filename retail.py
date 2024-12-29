# importing necessary package
import streamlit as st
import mysql.connector as m
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt

# setting layout for the app
st.title("Retail Order Analysis")

# creating a side bar for haing menus
with st.sidebar:
    selected = option_menu(
        menu_title = "Menu",
        options = ["Data Summary","Data Analysis"],
    )

# Defining layout and control for Data Summary page
if selected == "Data Summary":
    st.subheader("Data Summary")
    df = pd.read_csv("orders.csv.zip",compression = 'zip',encoding='utf-8',header=0)
    st.write(df.head(20))

# Defining layout and control for Data Analysis page
elif selected == "Data Analysis":
# connecting mysql server with python
    mydb = m.connect(
    host = "localhost",
    user = "root",
    password = "sathya",
    auth_plugin = "mysql_native_passwprd"
)

    mycursor = mydb.cursor()

    mycursor.execute("use Retail_Order")

#Creating two tabs in Data summary page, one for displaying mentor's query and another for displaying student's query
    mentor,student = st.tabs(["Mentor Query","Student Query"])

# Defining operations to be performed in mentor's query tab
    with mentor:
# Collected all queries and stored in a dictionary
        queries = {"Find top 10 highest revenue generating products":"select Product_Id, sum(Sale_Price) as sale from products group by Product_Id order by sale desc limit 10",
                   "Find the top 5 cities with the highest profit margins":"select o.City, sum(p.Profit) as total_profit from orders as o inner join products as p on o.Order_Id = p.Order_Id group by City order by total_profit desc limit 5",
                   "Calculate the total discount given for each category":"select Category , sum(Discount) as total_discount from products group by category",
                   "Find the average sale price per product category":"select Category, avg(Sale_Price) as avg_SP from products group by category",
                   "Find the region with the highest average sale price":"select o.Region, avg(p.Sale_Price) as avg_SP from orders as o inner join products as p on o.Order_Id = p.Order_Id group by Region order by avg_SP desc limit 1",
                   "Find the total profit per category":"select Category , sum(Profit) as total_profit from products group by category",
                   "Identify the top 3 segments with the highest quantity of orders":"select o.Segment, sum(p.Quantity) as total_quantity from orders as o inner join products as p on o.Order_Id = p.Order_Id group by Segment order by total_quantity desc limit 3",
                   "Determine the average discount percentage given per region":"select o.region, avg(p.Discount_Percent) as avg_Discount from orders as o inner join products as p on o.Order_Id = p.Order_Id group by Region",
                   "Find the product category with the highest total profit":"select category, sum(profit) as total_profit from products group by category order by total_profit desc limit 1",
                   "Calculate the total revenue generated per year":"select year(o.Order_Date) as year, sum(p.Profit) as total_revenue from orders as o inner join products as p on o.Order_Id = p.Order_Id group by year(Order_Date) order by year"
                  }
# Creating a selectbox with a list of all queries in the dictionary
        option = st.selectbox("Choose a query for analysis", list(queries.keys()),index=None)
        if option != None:
# executing the queries
            mycursor.execute(queries[option])
            data = mycursor.fetchall()
# converting the fetched result into a data frame and passing the data frame to web app
            df = pd.DataFrame(data, columns=[x[0] for x in mycursor.description])
            st.write(df)
# Creating line and pie charts based on the scenarios
            if option in ["Find top 10 highest revenue generating products","Find the top 5 cities with the highest profit margins"]:
                st.line_chart(df,x=df.columns[0],y=df.columns[1])
            elif option in ["Find the average sale price per product category","Calculate the total discount given for each category","Find the total profit per category","Identify the top 3 segments with the highest quantity of orders"]:
                fig,ax = plt.subplots()
                ax.pie(df[df.columns[1]], labels= df[df.columns[0]], autopct="%1.1f%%")
                ax.axis('equal')
                st.pyplot(fig)

#Defining operations to be performed in student query tab
    with student:

# Collected student's queries and stored in a dictionary
        
        queries = {
                   "Calculate total revenue generated by each product category over last 6 months" : """select p.Category, sum(p.Sale_Price) as total_revenue_for_last_6_months from orders as o inner join products as p on o.Order_Id = p.Order_Id where o.Order_Date >= (select max(Order_Date) from orders) - interval 6 month group by Category order by total_revenue_for_last_6_months desc""",
                   "Find 5 most popular products" : """select Sub_Category, sum(Quantity) as total_order_count from products group by Sub_Category order by total_order_count desc limit 5""",
                   "Calculate total no.of orders and revenue generated for each month" : """select month(o.Order_Date) as month, count(o.Order_Id) as order_count , sum(p.Sale_Price) as total_revenue from orders as o inner join products as p on o.Order_Id = p.Order_Id where o.Order_Date>= "2023-01-01" and o.Order_Date < "2024-01-01" group by month(o.Order_Date) order by month""",
                   "Find the time of the year with highest sales volume" : """select o.Order_Date, sum(p.Sale_Price) as Sale_price from orders as o inner join products as p on o.Order_Id = p.Order_Id group by Order_date order by Sale_price desc limit 3""",
            "Find the average quantity of products sold per order id" : """select o.Order_Id, avg(p.Quantity) as Avg_Quantity from orders as o inner join products as p on o.Order_Id = p.Order_Id group by Order_Id""",
        "Quantity of products sold under each category per year" : """select year(o.Order_Date) as year, p.category , count(p.Category) as product , sum(p.Quantity) as sold_units from orders as o inner join products as p on o.Order_Id = p.Order_Id group by year, p.Category order by year""", 
                "Find most used shipment mode" : """select Ship_Mode, count(Order_Id)as order_count from orders group by Ship_Mode order by order_count desc""",
                "Find Shipment mode which gives highest profit" : """select o.Ship_Mode, sum(p.Profit) as total_profit from orders as o inner join products as p on o.Order_Id = p.Order_Id group by Ship_Mode order by total_profit desc limit 3""",
                "Find average order value for each day of the week" : """select dayname(o.Order_Date) as day_of_week, sum(p.Sale_Price) as avg_sale from orders as o inner join products as p on o.Order_Id = p.Order_Id group by day_of_week order by avg_sale desc""",
                   "Popular product sold in each state" : """WITH RankedProducts AS (
    SELECT 
        o.State,
        p.Sub_Category as product,
        COUNT(p.Sub_Category) AS product_count,
        ROW_NUMBER() OVER (PARTITION BY o.State ORDER BY COUNT(p.Sub_Category) DESC) AS ranks
    FROM 
        orders o
    JOIN 
        products p ON o.Order_Id = p.Order_Id
    GROUP BY 
        o.State, p.Sub_Category
)
SELECT 
    State,
    product,
    product_count
FROM 
    RankedProducts
WHERE 
    ranks = 1
ORDER BY 
    State"""
        }
# Creating a selectbox with a list of all queries in the dictionary
        option = st.selectbox("Choose a query for analysis", list(queries.keys()),index=None)
        if option != None:
# executing the queries
            mycursor.execute(queries[option])
            data = mycursor.fetchall()
# converting the fetched result into a data frame and passing the data frame to web app
            df = pd.DataFrame(data, columns=[x[0] for x in mycursor.description])
            st.write(df)
# Creating line and pie charts based on the scenarios
        if option in ["Calculate total revenue generated by each product category over last 6 months","Find most used shipment mode"]:
                st.line_chart(df,x=df.columns[0],y=df.columns[1])
        elif option in ["Find Shipment mode which gives highest profit","Find average order value for each day of the week"]:
                fig,ax = plt.subplots()
                ax.pie(df[df.columns[1]], labels= df[df.columns[0]], autopct="%1.1f%%")
                ax.axis('equal')
                st.pyplot(fig)
# Closing the msql connection with python
    mycursor.close()
    mydb.close()