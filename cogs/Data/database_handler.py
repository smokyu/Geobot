import sqlite3
import os


class DatabaseHandler():
    def __init__(self, database_name: str):
        self.connection = sqlite3.connect(
            f"{os.path.dirname(os.path.abspath(__file__))}/{database_name}", timeout=10)
        self.connection.row_factory = sqlite3.Row

    def add_role(self, role_name: str, role_id: int):
        cursor = self.connection.cursor()
        query = "INSERT INTO Government (role_name, role_id) VALUES (?, ?);"
        cursor.execute(query, (role_name, role_id,))
        cursor.close()
        self.connection.commit()

    def remove_role(self, role_id: int):
        cursor = self.connection.cursor()
        query = "DELETE FROM Government WHERE role_id = ?;"
        cursor.execute(query, (role_id,))
        cursor.close()
        self.connection.commit()

    def get_role_name_list(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Government;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = map(dict, result)
        return result

    def add_candidate(self, user_id: int):
        cursor = self.connection.cursor()
        query = "INSERT INTO Candidate (user_id) VALUES (?)"
        cursor.execute(query, (user_id,))
        self.connection.commit()
        query = "SELECT * FROM Candidate;"
        cursor.execute(query)
        result = cursor.fetchall()

        try:
            result = map(dict, result)
        finally:
            for i in result:
                if i["user_id"] == user_id:
                    query = "UPDATE Candidate SET counter = ? WHERE user_id = ?;"
                    cursor.execute(query, (i["counter"] + 1, user_id))
                    cursor.close()
                    self.connection.commit()
                    return

    def remove_candidate(self, user_id: int):
        cursor = self.connection.cursor()
        query = "DELETE FROM Candidate WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        cursor.close()
        self.connection.commit()

    def reset_candidate_list(self):
        cursor = self.connection.cursor()
        query = "DELETE FROM Candidate;"
        cursor.execute(query)
        cursor.close()
        self.connection.commit()

    def get_candidate_list(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Candidate;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = map(dict, result)
        return result

    def create_account(self, user_id: int):
        cursor = self.connection.cursor()
        query = "INSERT INTO Wallet (user_id, balance) VALUES (?, ?);"
        cursor.execute(query, (user_id, 100))
        cursor.close()
        self.connection.commit()

    def create_accounts(self, user_ids: list):
        cursor = self.connection.cursor()
        query = "INSERT INTO Wallet (user_id, balance) VALUES (?, ?);"
        user_ids = list(map(lambda t_user_ids: (t_user_ids, 100), user_ids))
        cursor.executemany(query, user_ids)
        cursor.close()
        self.connection.commit()

    def delete_account(self, user_id: int):
        cursor = self.connection.cursor()
        query = "DELETE FROM Wallet WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        cursor.close()
        self.connection.commit()

    def get_account(self, user_id: int):
        cursor = self.connection.cursor()
        query = "SELECT balance FROM Wallet WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_account_list(self):
        cursor = self.connection.cursor()
        query = "SELECT user_id FROM Wallet;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = map(dict, result)
        return result

    def withdraw(self, user_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "SELECT balance FROM Wallet WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        try:
            balance = result[0]
        finally:
            query = "UPDATE Wallet SET balance = ? WHERE user_id = ?;"
            cursor.execute(query, (balance - amount, user_id))
            cursor.close()
            self.connection.commit()

    def deposit(self, user_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "SELECT balance FROM Wallet WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        try:
            balance = result[0]
        finally:
            query = "UPDATE Wallet SET balance = ? WHERE user_id = ?;"
            cursor.execute(query, (balance + amount, user_id))
            cursor.close()
            self.connection.commit()

    def add_item_to_items_list(self, item_name: str):
        cursor = self.connection.cursor()
        query = "INSERT INTO Items (item_name) VALUES (?);"
        cursor.execute(query, (item_name,))
        cursor.close()
        self.connection.commit()

    def remove_item_to_items_list(self, item_id: int):
        cursor = self.connection.cursor()
        query = "DELETE FROM Items WHERE item_id = ?;"
        cursor.execute(query, (item_id,))
        cursor.close()
        self.connection.commit()

    def get_item_id_by_item_name(self, item_name: str):
        cursor = self.connection.cursor()
        query = "SELECT item_id FROM Items WHERE item_name = ?;"
        cursor.execute(query, (item_name,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_item_name_by_item_id(self, item_id: str):
        cursor = self.connection.cursor()
        query = "SELECT item_name FROM Items WHERE item_id = ?;"
        cursor.execute(query, (item_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_inventory(self, user_id):
        cursor = self.connection.cursor()
        query = "SELECT Items.item_name, Inventory.amount FROM Inventory JOIN Items ON Inventory.item_id = Items.item_id WHERE Inventory.user_id = ?;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        result = list(map(dict, result))
        return result

    def add_item_to_inv(self, user_id: int, item_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "INSERT INTO Inventory (user_id, item_id, amount) VALUES (?, ?, ?);"
        cursor.execute(query, (user_id, item_id, amount))
        cursor.close()
        self.connection.commit()

    def add_amount_item_to_inv(self, user_id: int, item_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "SELECT amount FROM Inventory WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        try:
            current_amount = result[0]
        finally:
            query = "UPDATE Inventory SET amount = ? WHERE user_id = ?;"
            cursor.execute(query, (current_amount + amount, user_id))
            cursor.close()
            self.connection.commit()

    def remove_item_to_inv(self, user_id: int, item_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "SELECT amount FROM Inventory WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        try:
            current_amount = result[0]
        finally:
            query = "UPDATE Inventory SET amount = ? WHERE user_id = ? AND item_id = ?;"
            cursor.execute(query, (current_amount - amount, user_id, item_id))
            cursor.close()
            self.connection.commit()

    def delete_item_to_inv(self, user_id: int, item_id: int):
        cursor = self.connection.cursor()
        query = "DELETE FROM Inventory WHERE user_id = ? AND item_id = ?;"
        cursor.execute(query, (user_id, item_id))
        cursor.close()
        self.connection.commit()

    def add_member_to_db(self, user_id: int):
        cursor = self.connection.cursor()
        query = "INSERT INTO Members (user_id) VALUES (?);"
        cursor.execute(query, (user_id,))
        cursor.close()
        self.connection.commit()

    def add_members_to_db(self, user_ids: list):
        cursor = self.connection.cursor()
        query = "INSERT INTO Members (user_id) VALUES (?);"
        user_ids = list(map(lambda t_user_ids: (t_user_ids,), user_ids))
        cursor.executemany(query, user_ids)
        cursor.close()
        self.connection.commit()

    def remove_member_to_db(self, user_id: int):
        cursor = self.connection.cursor()
        query = "DELETE FROM Members WHERE user_id = ?;"
        cursor.execute(query, (user_id,))
        cursor.close()
        self.connection.commit()

    def check_member(self, user_id: int):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Candidate WHERE user_id= ?;"
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_members_list(self):
        cursor = self.connection.cursor()
        query = "SELECT user_id FROM Members;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = map(dict, result)
        return result

    def add_company_to_db(self, company_name: str, category: str):
        cursor = self.connection.cursor()
        query = "INSERT INTO Companys (company_name, category) VALUES (?, ?);"
        cursor.execute(query, (company_name.lower(), category))
        cursor.close()
        self.connection.commit()

    def remove_company_to_db(self, company_name: str):
        cursor = self.connection.cursor()
        query = "DELETE FROM Companys WHERE company_name = ?;"
        cursor.execute(query, (company_name.lower(),))
        cursor.close()
        self.connection.commit()

    def get_company_names(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Companys;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = map(dict, result)
        return result

    def get_company_names_list(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Companys;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_company_id_by_company_name(self, company_name: str):
        cursor = self.connection.cursor()
        query = "SELECT id FROM Companys WHERE company_name = ?;"
        cursor.execute(query, (company_name.lower(),))
        result = cursor.fetchone()
        cursor.close()
        return result

    def create_account_for_a_company(self, company_id: int):
        cursor = self.connection.cursor()
        query = "INSERT INTO Company_Wallet (company_id, balance) VALUES (?, ?);"
        cursor.execute(query, (company_id, 100))
        cursor.close()
        self.connection.commit()

    def get_company_account(self, company_id: int):
        cursor = self.connection.cursor()
        query = "SELECT balance FROM Company_Wallet WHERE company_id = ?;"
        cursor.execute(query, (company_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def get_company_inventory(self, company_id: int):
        cursor = self.connection.cursor()
        query = "SELECT Items.item_name, Company_Inventory.amount FROM Company_Inventory JOIN Items ON Company_Inventory.item_id = Items.item_id WHERE Company_Inventory.company_id = ?;"
        cursor.execute(query, (company_id,))
        result = cursor.fetchall()
        cursor.close()
        result = list(map(dict, result))
        return result

    def add_item_to_company_inv(self, company_id: int, item_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "INSERT INTO Company_Inventory (company_id, item_id, amount) VALUES (?, ?, ?);"
        cursor.execute(query, (company_id, item_id, amount))
        cursor.close()
        self.connection.commit()

    def add_amount_item_to_company_inv(self, company_id: int, item_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "SELECT amount FROM Company_Inventory WHERE company_id = ?;"
        cursor.execute(query, (company_id,))
        result = cursor.fetchone()

        try:
            current_amount = result[0]
        finally:
            query = "UPDATE Company_Inventory SET amount = ? WHERE company_id = ? AND item_id = ?;"
            cursor.execute(
                query, (current_amount + amount, company_id, item_id))
            cursor.close()
            self.connection.commit()

    def delete_item_to_company_inv(self, company_id: int, item_id: int):
        cursor = self.connection.cursor()
        query = "DELETE FROM Company_Inventory WHERE company_id = ? AND item_id = ?;"
        cursor.execute(query, (company_id, item_id))
        cursor.close()
        self.connection.commit()

    def remove_item_to_company_inv(self, company_id: int, item_id: int, amount: int):
        cursor = self.connection.cursor()
        query = "SELECT amount FROM Company_Inventory WHERE company_id = ?;"
        cursor.execute(query, (company_id,))
        result = cursor.fetchone()

        try:
            current_amount = result[0]
        finally:
            query = "UPDATE Company_Inventory SET amount = ? WHERE company_id = ? AND item_id = ?;"
            cursor.execute(
                query, (current_amount - amount, company_id, item_id))
            cursor.close()
            self.connection.commit()

    def create_recipe(self, recipe_name: str, items_id: list, amounts: list):
        cursor = self.connection.cursor()
        i = 0
        for item_id in items_id:
            query = "INSERT INTO Recipes (recipe_name, item_id, amount) VALUES (?, ?, ?);"
            cursor.execute(query, (recipe_name, item_id, amounts[i]))
            i += 1
        cursor.close()
        self.connection.commit()

    def delete_recipe(self, recipe_name: str):
        cursor = self.connection.cursor()
        query = "DELETE FROM Recipes WHERE recipe_name = ?;"
        cursor.execute(query, (recipe_name,))
        cursor.close()
        self.connection.commit()

    def get_recipe(self, recipe: str):
        cursor = self.connection.cursor()
        query = "SELECT Items.item_name, Recipes.amount FROM Recipes JOIN Items ON Recipes.item_id = Items.item_id WHERE Recipes.recipe_name = ?;"
        cursor.execute(query, (recipe,))
        result = cursor.fetchall()
        cursor.close()
        result = list(map(dict, result))
        return result

    def get_recipes(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Recipes;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = map(dict, result)
        return result

    def edit_brevet_time(self, numbers_of_days: int):
        obj = "Brevet"

        cursor = self.connection.cursor()
        query = "UPDATE Time SET number_of_days = ? WHERE obj = ?;"
        cursor.execute(
            query, (numbers_of_days, obj))
        cursor.close()
        self.connection.commit()

    def get_brevet_time(self):
        obj = "Brevet"

        cursor = self.connection.cursor()
        query = "SELECT number_of_days FROM Time WHERE obj = ?;"
        cursor.execute(query, (obj,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def edit_patent_status(self, patent_id: int, status: str):
        cursor = self.connection.cursor()
        query = "UPDATE Patents SET status = ? WHERE patent_id = ?;"
        cursor.execute(
            query, (status, patent_id))
        cursor.close()
        self.connection.commit()
        
    def get_patents(self):
        cursor = self.connection.cursor()
        query = "SELECT * from Patents;"
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        result = map(dict, result)
        return result
    
    def create_patent(self, patent_id: int, patent_name: str, timestamp: float):
        cursor = self.connection.cursor()
        query = "INSERT INTO Patents (patent_id, patent_name, status, activate_time) VALUES (?, ?, ?, ?);"
        cursor.execute(query, (patent_id, patent_name, "private", timestamp))
        cursor.close()
        self.connection.commit()
        
    def remove_patent_to_inventory(self, patent_id: str):
        cursor = self.connection.cursor()
        query = "DELETE FROM Inventory WHERE item_id = ?;"
        cursor.execute(query, (patent_id,))
        cursor.close()
        self.connection.commit()