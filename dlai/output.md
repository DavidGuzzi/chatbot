✅ Configuration loaded from .env file
🚀 Initializing Modern Data Chatbot...
✅ Data loaded: 200 rows
✅ Chatbot initialized successfully!

🤖 Testing chatbot with sample questions...

============================================================
🔍 TEST 1: ¿Cuál región tiene mejor performance en revenue?
============================================================
💡 **ANSWER:** The 'Este' region is currently the top-performing region in terms of revenue.

**Business Context:** The region with the highest total revenue indicates where the business is generating the most income. This insight can guide strategic decisions such as resource allocation, marketing focus, and expansion plans to capitalize on high-performing areas.

📊 **DATA (first 3 rows):**
   1. {'region': 'Este', 'total_revenue': 27630.169164659368}
🎯 **INSIGHTS:**
   • Investigate the strategies and practices employed in the 'Este' region to replicate success in other regions.
   • Increase investment in marketing and sales efforts in the 'Este' region to capitalize on its strong performance.
   • Conduct a detailed analysis of customer demographics and preferences in the 'Este' region to tailor products and services accordingly.

⚡ **PERFORMANCE:**
   • SQL: SELECT region, SUM(revenue) AS total_revenue
FROM tiendas
GROUP BY region
ORDER BY total_revenue DESC
LIMIT 1;
   • Time: 17.89s
   • Cached: No
   • Confidence: 0.95

============================================================

============================================================
🔍 TEST 2: ¿El experimento tuvo impacto positivo?
============================================================
💡 **ANSWER:** The experiment had a positive impact, with Experimento_C showing the highest improvement in both conversion rate and average revenue compared to the control group.

**Business Context:** The results will show whether the experimental changes led to higher conversion rates and revenue compared to the control group. A higher average conversion rate and revenue in the experiment groups would suggest a positive impact of the experiment on business performance.

📊 **DATA (first 3 rows):**
   1. {'experimento': 'Experimento_C', 'avg_conversion_rate': 11.778199999999995, 'avg_revenue': 516.0333354867872}
   2. {'experimento': 'Experimento_B', 'avg_conversion_rate': 10.0574, 'avg_revenue': 483.86003795431947}
   3. {'experimento': 'Experimento_A', 'avg_conversion_rate': 9.5266, 'avg_revenue': 431.0726650696733}
   ... and 1 more rows

🎯 **INSIGHTS:**
   • Consider scaling the strategies used in Experimento_C across other segments or markets to maximize revenue.
   • Conduct a deeper analysis of the specific elements in Experimento_C that contributed to its success to replicate them in future experiments.
   • Allocate more resources to optimize and enhance the strategies used in Experimento_C for even better results.

⚡ **PERFORMANCE:**
   • SQL: SELECT experimento, AVG(conversion_rate) AS avg_conversion_rate, AVG(revenue) AS avg_revenue
FROM tiendas
GROUP BY experimento
ORDER BY avg_conversion_rate DESC, avg_revenue DESC
LIMIT 10;
   • Time: 7.25s
   • Cached: No
   • Confidence: 0.95

============================================================

============================================================
🔍 TEST 3: ¿Qué tipo de tienda convierte mejor?
============================================================
💡 **ANSWER:** Mall stores have the highest average conversion rate, making them the most effective type of store for converting visitors into buyers.

**Business Context:** Understanding which type of store converts better can help the business allocate resources more effectively, optimize marketing strategies, and improve overall sales performance. By focusing on store types with higher conversion rates, the business can enhance customer engagement and increase revenue.

📊 **DATA (first 3 rows):**
   1. {'tipo_tienda': 'Mall', 'avg_conversion_rate': 10.317162162162159, 'total_conversiones': 1702, 'num_tiendas': 74}
   2. {'tipo_tienda': 'Street', 'avg_conversion_rate': 10.123835616438356, 'total_conversiones': 1662, 'num_tiendas': 73}
   3. {'tipo_tienda': 'Outlet', 'avg_conversion_rate': 9.661132075471697, 'total_conversiones': 1201, 'num_tiendas': 53}
🎯 **INSIGHTS:**
   • Invest in enhancing the customer experience in mall stores to further boost conversion rates.
   • Consider strategies to improve the conversion rates of outlet stores, such as targeted promotions or improved store layouts.
   • Analyze the factors contributing to the high conversion rates in mall stores and apply these insights to other store types.
   • Conduct customer feedback sessions in street and outlet stores to identify potential areas for improvement.

⚡ **PERFORMANCE:**
   • SQL: SELECT tipo_tienda, AVG(conversion_rate) as avg_conversion_rate, SUM(conversiones) as total_conversiones, COUNT(*) as num_tiendas
FROM tiendas
GROUP BY tipo_tienda
ORDER BY avg_conversion_rate DESC
LIMIT 10;
   • Time: 7.49s
   • Cached: No
   • Confidence: 0.95

============================================================

============================================================
🔍 TEST 4: Muéstrame las top 3 tiendas por conversion rate
============================================================
💡 **ANSWER:** The store with the highest conversion rate is T_Experimento_C_016, indicating it is the most effective at turning visitors into customers.

**Business Context:** Identifying the top 3 stores by conversion rate can provide insights into which stores are most effective at converting visitors into customers. This information can be used to analyze successful strategies or practices that could be implemented in other stores to improve overall performance.

📊 **DATA (first 3 rows):**
   1. {'tienda_id': 'T_Experimento_C_016', 'conversion_rate': 18.25}
   2. {'tienda_id': 'T_Experimento_C_008', 'conversion_rate': 16.68}
   3. {'tienda_id': 'T_Experimento_C_002', 'conversion_rate': 16.48}
🎯 **INSIGHTS:**
   • Investigate the strategies and practices employed by T_Experimento_C_016 to understand what contributes to its high conversion rate.
   • Consider implementing similar strategies in other stores to potentially increase their conversion rates.
   • Analyze customer feedback and satisfaction scores for T_Experimento_C_016 to identify any unique customer service practices.
   • Conduct A/B testing in other stores to determine if changes inspired by T_Experimento_C_016's practices lead to improved conversion rates.

⚡ **PERFORMANCE:**
   • SQL: SELECT tienda_id, conversion_rate 
FROM tiendas
ORDER BY conversion_rate DESC
LIMIT 3;
   • Time: 9.00s
   • Cached: No
   • Confidence: 0.95

============================================================

============================================================
🔍 TEST 5: ¿Hay diferencias entre Mall y Street stores?
============================================================
💡 **ANSWER:** Mall stores slightly outperform Street stores in terms of conversion rates and total conversions, despite having a marginally lower average revenue per store.

**Business Context:** Understanding the performance differences between 'Mall' and 'Street' stores can guide strategic decisions on where to focus marketing efforts, resource allocation, and potential expansion. If one type consistently outperforms the other, it may indicate a more lucrative business model or customer preference.

📊 **DATA (first 3 rows):**
   1. {'tipo_tienda': 'Street', 'tiendas': 73, 'avg_revenue': 461.580397876001, 'avg_conversion_rate': 10.123835616438356, 'total_usuarios': 16460, 'total_conversiones': 1662}
   2. {'tipo_tienda': 'Mall', 'tiendas': 74, 'avg_revenue': 454.26325854063197, 'avg_conversion_rate': 10.317162162162159, 'total_usuarios': 16680, 'total_conversiones': 1702}
🎯 **INSIGHTS:**
   • Investigate the factors contributing to the higher conversion rate in Mall stores and consider implementing similar strategies in Street stores.
   • Explore opportunities to increase average revenue per store in Mall locations, possibly through upselling or cross-selling strategies.
   • Leverage the higher foot traffic in Mall stores by optimizing store layouts and enhancing customer experience to further boost conversions.

⚡ **PERFORMANCE:**
   • SQL: SELECT tipo_tienda, COUNT(*) as tiendas, AVG(revenue) as avg_revenue, AVG(conversion_rate) as avg_conversion_rate, SUM(usuarios) as total_usuarios, SUM(conversiones) as total_conversiones
FROM tiendas
WHERE tipo_tienda IN ('Mall', 'Street')
GROUP BY tipo_tienda
ORDER BY avg_revenue DESC
LIMIT 10;
   • Time: 12.60s
   • Cached: No
   • Confidence: 0.95

============================================================

📈 **CACHE PERFORMANCE:**
   • Cached queries: 5
   • Cache hits: 0
   • Hit rate: 0.0%

🎉 Testing completed!

============================================================
🔄 INTERACTIVE MODE - Ask your own questions!
(Type 'quit' to exit)
============================================================

❓ Your question: ¿Cuántas tiendas control han sido analizadas?

🤖 Processing: ¿Cuántas tiendas control han sido analizadas?

💡 **Answer:** A total of 50 control stores have been analyzed, indicating a comprehensive evaluation of the control segment within the retail network.

**Business Context:** Understanding the number of control stores is crucial for evaluating the baseline performance against which experimental changes are measured. This helps in assessing the impact of any interventions or changes implemented in experimental stores.

📊 **Data sample:**
   1. {'control_store_count': 50}

⚡ Time: 6.60s | Cached: No

❓ Your question: ¿Cuántos usuarios en total hay en las tiendas control?

🤖 Processing: ¿Cuántos usuarios en total hay en las tiendas control?

💡 **Answer:** The total number of users in the control stores is 11,196, indicating a significant customer base that can be leveraged for targeted marketing and engagement strategies.

**Business Context:** Understanding the total number of users in control stores is crucial for comparing the performance of experimental stores against a baseline. This helps in assessing the impact of any changes or experiments conducted in other stores.

📊 **Data sample:**
   1. {'total_usuarios_control': 11196}

⚡ Time: 6.03s | Cached: No

❓ Your question: ¿Cuántas tiendas control tipo mall situadas al este existen?

🤖 Processing: ¿Cuántas tiendas control tipo mall situadas al este existen?

💡 **Answer:** There are currently 7 mall-type stores located in the eastern region.

**Business Context:** Understanding the number of control group stores of a specific type and location helps in analyzing the distribution and performance of different store types across regions. This insight can guide strategic decisions regarding resource allocation, marketing efforts, and operational focus.

📊 **Data sample:**
   1. {'num_tiendas': 7}

⚡ Time: 7.61s | Cached: No

❓ Your question: En promedio, ¿cuántas conversiones se dan en tiendas control tipo mall situadas al este?

🤖 Processing: En promedio, ¿cuántas conversiones se dan en tiendas control tipo mall situadas al este?

💡 **Answer:** There are currently 7 mall-type stores located in the eastern region.

**Business Context:** Understanding the number of control group stores of a specific type and location helps in analyzing the distribution and performance of different store types across regions. This insight can guide strategic decisions regarding resource allocation, marketing efforts, and operational focus.

📊 **Data sample:**
   1. {'num_tiendas': 7}

⚡ Time: 0.04s | Cached: Yes

❓ Your question: En promedio, ¿cuántas conversiones se dan en tiendas control tipo mall situadas al este?

🤖 Processing: En promedio, ¿cuántas conversiones se dan en tiendas control tipo mall situadas al este?

💡 **Answer:** There are currently 7 mall-type stores located in the eastern region.

**Business Context:** Understanding the number of control group stores of a specific type and location helps in analyzing the distribution and performance of different store types across regions. This insight can guide strategic decisions regarding resource allocation, marketing efforts, and operational focus.

📊 **Data sample:**
   1. {'num_tiendas': 7}

⚡ Time: 0.01s | Cached: Yes

❓ Your question: ¿Cuántas conversiones se dan en promedio en las tiendas control tipo mall del este?        

🤖 Processing: ¿Cuántas conversiones se dan en promedio en las tiendas control tipo mall del este?

💡 **Answer:** The average number of conversions in mall-type control stores in the east region is approximately 22 per period.

**Business Context:** Understanding the average number of conversions in control stores of type mall in the east region helps in assessing the baseline performance of these stores. This information can be used to compare against experimental stores or other regions to evaluate the effectiveness of marketing strategies or operational changes.

📊 **Data sample:**
   1. {'avg_conversiones': 21.714285714285715}

⚡ Time: 7.10s | Cached: No

❓ Your question: quit
👋 Goodbye!




✅ All files and configuration ready
🚀 Initializing Modern Data Chatbot with Multiple Tables...
✅ Maestro loaded: 200 stores
✅ Data loaded: 200 rows in tiendas table
✅ Chatbot initialized with both tables!

🤖 Testing chatbot with multi-table questions...

======================================================================
🔍 TEST 1: ¿Cuáles son las tiendas con mejor performance? Muestra el nombre de la tienda
======================================================================
💡 **ANSWER:** Tienda Express 002 is currently the top-performing store in terms of revenue, while Megastore Oeste 016 leads in conversion rate.

**Business Context:** The query identifies the top 10 stores based on their financial performance, specifically focusing on revenue and conversion rate. This information is crucial for business stakeholders to understand which stores are excelling and potentially replicate their strategies across other locations.

📊 **DATA (first 3 rows):**
   1. {'nombre_tienda': 'Tienda Express 002', 'revenue': 1006.3890417515818, 'conversion_rate': 16.48}
   2. {'nombre_tienda': 'Megastore Oeste 016', 'revenue': 983.7496521472317, 'conversion_rate': 18.25}
   3. {'nombre_tienda': 'Galería Este 005', 'revenue': 899.1693417325835, 'conversion_rate': 14.28}
   ... and 7 more rows

📝 **SQL USED:**
   SELECT m.nombre_tienda, t.revenue, t.conversion_rate
FROM tiendas t
JOIN maestro_tiendas m ON t.tienda_id = m.tienda_id
ORDER BY t.revenue DESC, t.conversion_rate DESC
LIMIT 10;

🎯 **INSIGHTS:**
   • Investigate the strategies employed by Tienda Express 002 to replicate its revenue success across other stores.
   • Analyze customer engagement and marketing tactics at Megastore Oeste 016 to understand the high conversion rate.
   • Consider cross-training staff from lower-performing stores with teams from Tienda Express 002 and Megastore Oeste 016.
   • Implement targeted promotions or loyalty programs to boost conversion rates in stores with lower performance.

⚡ **PERFORMANCE:**
   • Time: 8.45s
   • Cached: No
   • Confidence: 0.95

======================================================================

======================================================================
🔍 TEST 2: ¿Qué gerente maneja las tiendas con mayor revenue?
======================================================================
💡 **ANSWER:** Gerente_1406 manages the stores with the highest total revenue, indicating strong performance in revenue generation compared to peers.

**Business Context:** This query helps identify which managers are overseeing the most financially successful stores. Understanding which managers are driving higher revenues can inform decisions on best practices, training, and resource allocation. It can also highlight successful management strategies that could be replicated across other stores.

📊 **DATA (first 3 rows):**
   1. {'gerente': 'Gerente_1406', 'total_revenue': 1006.3890417515818}
   2. {'gerente': 'Gerente_8119', 'total_revenue': 983.7496521472317}
   3. {'gerente': 'Gerente_2832', 'total_revenue': 971.6374334996947}
   ... and 7 more rows

📝 **SQL USED:**
   SELECT m.gerente, SUM(t.revenue) AS total_revenue
FROM tiendas t
JOIN maestro_tiendas m ON t.tienda_id = m.tienda_id
GROUP BY m.gerente
ORDER BY total_revenue DESC
LIMIT 10;

🎯 **INSIGHTS:**
   • Conduct a detailed analysis of Gerente_1406's strategies and practices to identify key success factors that can be replicated across other stores.
   • Implement targeted training programs for other managers based on the successful practices of Gerente_1406.
   • Consider incentivizing Gerente_1406 to share insights and mentor other managers to elevate overall performance.
   • Explore opportunities to expand the market reach of stores managed by Gerente_1406, leveraging their proven success.

⚡ **PERFORMANCE:**
   • Time: 6.90s
   • Cached: No
   • Confidence: 0.95

======================================================================

======================================================================
🔍 TEST 3: Muéstrame las top 5 tiendas por conversion rate con sus nombres y gerentes
======================================================================
💡 **ANSWER:** The store 'Megastore Oeste 016' has the highest conversion rate among the top 5 stores, indicating a strong ability to convert visitors into customers.

**Business Context:** Identifying the top 5 stores by conversion rate helps the business understand which stores are most effective at converting visitors into customers. This insight can guide resource allocation, marketing strategies, and operational improvements to replicate success across other stores.

📊 **DATA (first 3 rows):**
   1. {'tienda_id': 'T_Experimento_C_016', 'nombre_tienda': 'Megastore Oeste 016', 'gerente': 'Gerente_8119', 'conversion_rate': 18.25}
   2. {'tienda_id': 'T_Experimento_C_008', 'nombre_tienda': 'Centro Premium 008', 'gerente': 'Gerente_6000', 'conversion_rate': 16.68}
   3. {'tienda_id': 'T_Experimento_C_002', 'nombre_tienda': 'Tienda Express 002', 'gerente': 'Gerente_1406', 'conversion_rate': 16.48}
   ... and 2 more rows

📝 **SQL USED:**
   SELECT t.tienda_id, m.nombre_tienda, m.gerente, t.conversion_rate
FROM tiendas t
JOIN maestro_tiendas m ON t.tienda_id = m.tienda_id
ORDER BY t.conversion_rate DESC
LIMIT 5;

🎯 **INSIGHTS:**
   • Investigate the strategies employed by 'Megastore Oeste 016' to understand what contributes to its high conversion rate and consider replicating these strategies in other stores.
   • Conduct training sessions led by Gerente_8119 to share best practices and insights with managers from other stores.
   • Enhance marketing efforts and customer engagement strategies in stores with lower conversion rates to improve their performance.
   • Evaluate the customer experience and sales processes at 'Centro Premium 008' and 'Tienda Express 002' to identify potential areas for improvement.

⚡ **PERFORMANCE:**
   • Time: 7.19s
   • Cached: No
   • Confidence: 0.95

======================================================================

======================================================================
🔍 TEST 4: ¿Hay algún patrón entre el tipo de tienda y el nombre que se le asigna?
======================================================================
💡 **ANSWER:** There is a noticeable pattern where store names often include a reference to their type, such as 'Plaza' for malls and 'Shopping' for street stores.

**Business Context:** Understanding the relationship between store names and types can provide insights into branding strategies and customer perception. If certain store types consistently have specific naming conventions, it might reflect a targeted branding approach or customer expectation alignment.

📊 **DATA (first 3 rows):**
   1. {'nombre_tienda': 'Plaza Central 021', 'tipo_tienda': 'Mall', 'count': 2}
   2. {'nombre_tienda': 'Shopping Boulevard 028', 'tipo_tienda': 'Street', 'count': 2}
   3. {'nombre_tienda': 'Plaza Mayor 030', 'tipo_tienda': 'Outlet', 'count': 2}
   ... and 7 more rows

📝 **SQL USED:**
   SELECT m.nombre_tienda, t.tipo_tienda, COUNT(*) as count
FROM tiendas t
JOIN maestro_tiendas m ON t.tienda_id = m.tienda_id
GROUP BY m.nombre_tienda, t.tipo_tienda
ORDER BY count DESC
LIMIT 10;

🎯 **INSIGHTS:**
   • Consider standardizing store naming conventions to include clear references to their type, enhancing brand recognition and customer navigation.
   • Explore marketing strategies that leverage the naming conventions to attract specific customer demographics associated with each store type.
   • Conduct customer surveys to understand if the naming conventions influence shopping behavior and brand perception.

⚡ **PERFORMANCE:**
   • Time: 10.27s
   • Cached: No
   • Confidence: 0.9

======================================================================

======================================================================
🔍 TEST 5: ¿Las tiendas abiertas en 2020 tienen mejor performance que las otras?
======================================================================
💡 **ANSWER:** Stores opened in 2020 generally show strong performance, with some outperforming others in terms of average revenue and conversion rates.

**Business Context:** Understanding whether stores opened in 2020 perform better can guide future decisions on store openings, resource allocation, and marketing strategies. If 2020 stores show better performance, it might indicate successful strategies or favorable market conditions during that period.

📊 **DATA (first 3 rows):**
   1. {'nombre_tienda': 'Tienda Express 002', 'fecha_apertura': datetime.date(2020, 3, 14), 'avg_revenue': 1006.3890417515818, 'avg_conversion_rate': 16.48}
   2. {'nombre_tienda': 'Megastore Oeste 016', 'fecha_apertura': datetime.date(2020, 1, 4), 'avg_revenue': 983.7496521472317, 'avg_conversion_rate': 18.25}
   3. {'nombre_tienda': 'Galería Este 005', 'fecha_apertura': datetime.date(2020, 1, 24), 'avg_revenue': 899.1693417325835, 'avg_conversion_rate': 14.28}
   ... and 7 more rows

📝 **SQL USED:**
   SELECT 
    m.nombre_tienda, 
    m.fecha_apertura, 
    AVG(t.revenue) AS avg_revenue, 
    AVG(t.conversion_rate) AS avg_conversion_rate
FROM 
    tiendas t
JOIN 
    maestro_tiendas m ON t.tienda_id = m.tienda_id
WHERE 
    EXTRACT(YEAR FROM m.fecha_apertura) = 2020
GROUP BY 
    m.nombre_tienda, m.fecha_apertura
ORDER BY 
    avg_revenue DESC
LIMIT 10;

🎯 **INSIGHTS:**
   • Conduct a detailed analysis of Tienda Express 002 and Megastore Oeste 016 to identify successful strategies that can be replicated across other stores.
   • Implement targeted marketing campaigns to improve conversion rates for stores with lower performance, such as Tienda Principal 014.
   • Explore operational efficiencies and customer engagement strategies that contribute to higher revenues in top-performing stores.

⚡ **PERFORMANCE:**
   • Time: 7.94s
   • Cached: No
   • Confidence: 0.9

======================================================================

======================================================================
🔍 TEST 6: Compara el performance entre Mall Norte vs Plaza Central
======================================================================
💡 **ANSWER:** Mall Norte outperforms Plaza Central in terms of average revenue and conversion rate, indicating a stronger sales performance.

**Business Context:** This query helps the business understand which store type and location combination is more profitable. By comparing 'Mall' stores in the 'Norte' region with 'Plaza Central 041', the business can make informed decisions about resource allocation, marketing strategies, and potential expansion plans based on revenue and conversion performance.

📊 **DATA (first 3 rows):**
   1. {'region': 'Norte', 'tipo_tienda': 'Street', 'num_tiendas': 1, 'avg_revenue': 586.02961347247, 'avg_conversion_rate': 10.37}
   2. {'region': 'Norte', 'tipo_tienda': 'Mall', 'num_tiendas': 16, 'avg_revenue': 450.95817246595624, 'avg_conversion_rate': 11.225}
   3. {'region': 'Sur', 'tipo_tienda': 'Mall', 'num_tiendas': 1, 'avg_revenue': 272.13354017314066, 'avg_conversion_rate': 6.23}
📝 **SQL USED:**
   SELECT 
    t.region, 
    t.tipo_tienda, 
    COUNT(t.tienda_id) AS num_tiendas, 
    AVG(t.revenue) AS avg_revenue, 
    AVG(t.conversion_rate) AS avg_conversion_rate
FROM 
    tiendas t
JOIN 
    maestro_tiendas m ON t.tienda_id = m.tienda_id
WHERE 
    (t.tipo_tienda = 'Mall' AND t.region = 'Norte') OR m.nombre_tienda = 'Plaza Central 041'
GROUP BY 
    t.region, t.tipo_tienda
ORDER BY 
    avg_revenue DESC
LIMIT 10;

🎯 **INSIGHTS:**
   • Consider expanding the number of stores in Mall Norte to capitalize on its higher performance.
   • Investigate the factors contributing to Mall Norte's higher conversion rate and apply similar strategies to Plaza Central.
   • Enhance marketing efforts in Plaza Central to boost visibility and sales, potentially increasing its conversion rate.

⚡ **PERFORMANCE:**
   • Time: 8.25s
   • Cached: No
   • Confidence: 0.95

======================================================================

📋 **DATABASE SCHEMA INFORMATION:**
Available tables: ['maestro_tiendas', 'tiendas']
  - maestro_tiendas: ['tienda_id', 'nombre_tienda', 'fecha_apertura', 'gerente']
  - tiendas: ['experimento', 'tienda_id', 'region', 'tipo_tienda', 'usuarios', 'conversiones', 'revenue', 'conversion_rate']

Relationships: {'tiendas.tienda_id': 'maestro_tiendas.tienda_id', 'description': 'tiendas table contains transaction data, maestro_tiendas contains store master data'}

📈 **CACHE PERFORMANCE:**
   • Cached queries: 6
   • Cache hits: 0
   • Hit rate: 0.0%

🎉 Multi-table testing completed!

🔧 **MANUAL VERIFICATION:**
Let's verify the JOIN is working correctly...
Manual query result: [{'tienda_id': 'T_Control_001', 'nombre_tienda': 'Plaza Central 001'}, {'tienda_id': 'T_Control_002', 'nombre_tienda': 'Mall Norte 002'}]
SQL used: SELECT t.tienda_id, m.nombre_tienda
FROM tiendas t
JOIN maestro_tiendas m ON t.tienda_id = m.tienda_id
LIMIT 3;