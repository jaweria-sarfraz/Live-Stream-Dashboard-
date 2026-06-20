import os
import re
import webbrowser
import pyodbc # SQL Server se connect karne ke liye

def generate_dashboard(query):
    # 1. SQL Server Connection Setup
    # Note: 'localhost' aur 'ProductSales' database ka use ho raha hai jo aapne SSMS mein banaya tha
   # 1. Updated SQL Server Connection Setup
   # 1. SQL Server Connection Setup (Configured for your SSMS)
    conn_str = (
        "DRIVER={SQL Server};"
        "SERVER=DESKTOP-APADBTF\\SQLEXPRESS;"
        "DATABASE=dashboardDB;"                       # Naya database name
        "Trusted_Connection=yes;"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        
        # 2. Data Calculation for Analytics Cards
        total_orders = len(rows)
        gross_revenue = 0
        active_projects = 0
        
        table_rows_html = ""
        
        # 3. Dynamic HTML Generation Loop
        for row in rows:
            # Data map kar rahe hain (ID, ItemName, Category, Price, Status)
            row_dict = dict(zip(columns, row))
            
            p_id = row_dict.get('ProductID', '-')
            name = row_dict.get('ItemName', '-')
            category = row_dict.get('Category', '-')
            price = row_dict.get('Price', 0)
            status = row_dict.get('Status', 'Pending')
            
            gross_revenue += price
            if status.lower() == 'completed':
                active_projects += 1
                status_class = "status-completed"
            else:
                status_class = "status-pending"
                
            # HTML Table Row Injection
            table_rows_html += f"""
            <tr>
                <td>{p_id}</td>
                <td>{name}</td>
                <td>{category}</td>
                <td>{price:,}</td>
                <td><span class="status-pill {status_class}">{status}</span></td>
            </tr>
            """
            
        conn.close()
        
        # 4. Asli HTML File ko update karna
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # Regex ke zariye values ko HTML mein replace karna
        html_content = re.sub(r'<div class="card-value">04</div>', f'<div class="card-value">{total_orders:02d}</div>', html_content)
        html_content = re.sub(r'<div class="card-value">90,000</div>', f'<div class="card-value">{gross_revenue:,}</div>', html_content)
        html_content = re.sub(r'<div class="card-value">03</div>', f'<div class="card-value">{active_projects:02d}</div>', html_content)
        
        # Table Body replace karna
        html_content = re.sub(r'<tbody id="data-rows">.*?</tbody>', f'<tbody id="data-rows">{table_rows_html}</tbody>', html_content, flags=re.DOTALL)
        
        # Nayi output file save karna
        output_path = os.path.abspath("live_dashboard.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Browser mein auto-open karna
        webbrowser.open(f"file://{output_path}")
        print("SUCCESS: Dashboard Generated Successfully!")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

# Testing ke liye query pass kar ke check karte hain
if __name__ == "__main__":
    import sys
    import os

    # ---- YEH LINE MASLA DEEWAR SE KHATAM KAR DE GI ----
    # Python ko jabran uske apne folder mein bhej dena jahan index.html pari hai
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    query = "SELECT * FROM ProductSales;"
    
    try:
        generate_dashboard(query)
    except Exception as e:
        import traceback
        print("\n--- CRITICAL ERROR ---")
        print(traceback.format_exc())
        print("----------------------")
        input("\nWindow ko rokne ke liye ENTER dabayein...")