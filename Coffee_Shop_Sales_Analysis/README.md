# ☕ End-to-End Sales Analytics Dashboard — Coffee Shop

Analysis of **149,116 coffee-shop transactions** (Jan–Jun 2023) across
3 store locations, 9 product categories, and 29 product types — from raw
MySQL data to an interactive Power BI dashboard.

## Business questions answered
- How are sales, orders, and quantity trending month over month?
- Which stores, categories, and products drive revenue?
- When do customers buy — which days, which hours?
- How do weekdays compare to weekends?

## SQL analysis (15+ queries — see CoffeeShop.sql)
- **Month-over-month growth %** using the `LAG()` window function
- **Above/below-average day classification** using `AVG() OVER ()`
  with a `CASE` expression
- Weekday vs weekend segmentation, hourly sales breakdowns
- KPI aggregations: Total Sales, Total Orders, Total Quantity Sold

Example — MoM sales growth:
    SELECT MONTH(transaction_date) AS month,
           ROUND(SUM(unit_price * transaction_qty)) AS total_sales,
           (SUM(unit_price * transaction_qty)
             - LAG(SUM(unit_price * transaction_qty), 1)
               OVER (ORDER BY MONTH(transaction_date)))
             / LAG(SUM(unit_price * transaction_qty), 1)
               OVER (ORDER BY MONTH(transaction_date)) * 100
           AS mom_increase_pct
    FROM coffee_shop_sales
    GROUP BY MONTH(transaction_date);

## Power BI dashboard
2 pages: main dashboard + a custom **tooltip page** (Day & Hour detail
on hover). 11 KPI cards, MoM trend lines, donut charts for weekday/weekend
mix, bar charts by location / category / product, calendar slicer.

## Key insights
- Clear month-over-month sales growth across the period
- Morning hours are the revenue peak — staffing and stock should follow
- Weekday sales dominate weekend sales in total revenue
- Coffee and Tea categories lead; top 10 product types identified

## Files
- `Coffee_Shop_Sales.csv` — source data (149K rows, 11 columns)
- `CoffeeShop.sql` — all analysis queries
- `CoffeeShopDashboard.pbix` — Power BI dashboard

## Tools
MySQL · Power BI (DAX, Power Query, custom tooltips) · SQL window functions
