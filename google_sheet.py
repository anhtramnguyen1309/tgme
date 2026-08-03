from __future__ import annotations

import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound
from datetime import datetime, timedelta
from config import DEFAULT_TRIAL_DAYS
from config import SHEET_ID
from typing import Dict
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheet:

    def __init__(self):

        creds = Credentials.from_service_account_file(
            "credentials.json",
            scopes=SCOPES
        )

        client = gspread.authorize(creds)

        self.book = client.open_by_key(SHEET_ID)

        self.users_sheet = self._get_or_create_users_sheet()
        self.logs_sheet = self._get_or_create_logs_sheet()
        self.settings_sheet = self._get_or_create_settings_sheet()

        self.users_cache = []
        self.settings_cache = {}

        self.refresh()

    # ==================================================
    # CREATE SHEETS
    # ==================================================

    def _get_or_create_users_sheet(self):

        try:
            ws = self.book.worksheet("Users")

        except WorksheetNotFound:

            ws = self.book.add_worksheet(
                title="Users",
                rows=1000,
                cols=20
            )

            ws.append_row([
                "user_id",
                "name",
                "username",
                "first_use",
                "expiry",
                "status",
                "query_count",
                "last_query",
                "created_by",
                "note",
               
])

        return ws

    def _get_or_create_logs_sheet(self):

        try:
            ws = self.book.worksheet("Logs")

        except WorksheetNotFound:

            ws = self.book.add_worksheet(
                title="Logs",
                rows=5000,
                cols=10
            )

            ws.append_row([
                "time",
                "user_id",
                "command",
                "result",
            ])

        return ws

    def _get_or_create_settings_sheet(self):

        try:
            ws = self.book.worksheet("Settings")

        except WorksheetNotFound:

            ws = self.book.add_worksheet(
                title="Settings",
                rows=100,
                cols=5
            )

            ws.append_row([
                "key",
                "value",
            ])

            ws.append_row([
                "trial_days",
                "10",
            ])

            ws.append_row([
                "version",
                "2.0",
            ])

        return ws

    # ==================================================
    # CACHE
    # ==================================================

    from typing import Dict

        

    def refresh(self):

        self.users_cache = self.users_sheet.get_all_records()

       # Cache user theo ID
        self.user_cache = {}

        # Index user_id -> row
        self.user_index: Dict[str, int] = {}

        for i, user in enumerate(self.users_cache, start=2):

            uid = str(user["user_id"])

            self.user_cache[uid] = user
            self.user_index[uid] = i

        settings = self.settings_sheet.get_all_records()

        self.settings_cache = {
           row["key"]: row["value"]
           for row in settings
    }

    def user_exists(self, user_id: int) -> bool:
       return str(user_id) in self.user_index   

    def get_user(self, user_id: int):
      return self.user_cache.get(str(user_id))

    
    

    def register_user(
       self,
       user_id: int,
       full_name: str,
       username: str = "",
):

       if self.user_exists(user_id):
          return False

       today = datetime.now()

       trial_days = int(
           self.get_setting(
               "trial_days",
               DEFAULT_TRIAL_DAYS,)
    )

       expiry = today + timedelta(days=trial_days)

       row = [
            user_id,
            full_name,
            username,
            today.strftime("%Y-%m-%d"),
            expiry.strftime("%Y-%m-%d"),
            "trial",
            0,
            "",
            "bot",
            "",
            
    ]

       self.users_sheet.append_row(row)

       self.refresh()

       return True


    def delete_user(self, user_id: int):

        row = self.get_row(user_id)

        if row:

           self.users_sheet.delete_rows(row)

           self.refresh()   



    def get_row(self, user_id: int):

       return self.user_index.get(str(user_id))

    def get_all_users(self):

       return self.users_cache
       
    def get_setting(self, key, default=None):

        return self.settings_cache.get(key, default)

    def set_setting(self, key, value):

        values = self.settings_sheet.get_all_values()

        for i, row in enumerate(values):

            if i == 0:
                continue

            if row[0] == key:

                self.settings_sheet.update_cell(
                    i + 1,
                    2,
                    str(value)
                )

                self.refresh()

                return

        self.settings_sheet.append_row([
            key,
            str(value),
        ])

        self.refresh()

    # ==================================================
    # CACHE HELPERS
    # ==================================================

    def reload(self):
        self.refresh()

    def users(self):
        return self.users_cache

    def settings(self):
        return self.settings_cache


        # ==================================================
    # UPDATE USER
    # ==================================================

    def update_value(self, user_id, column, value):

        row = self.get_row(user_id)

        if not row:
            return False

        headers = self.users_sheet.row_values(1)

        if column not in headers:
            return False

        col = headers.index(column) + 1

        self.users_sheet.update_cell(
            row,
            col,
            value
        )

        # update cache luôn
        uid = str(user_id)

        if uid in self.user_cache:
            self.user_cache[uid][column] = value

        self.refresh()

        return True


    # ==================================================
    # QUERY
    # ==================================================

    def increase_query(self, user_id):

        user = self.get_user(user_id)

        if not user:
            return False

        return self.update_user(
            user_id,
            query_count=int(user["query_count"]) + 1
        )

    def update_last_query(self, user_id, command):

        return self.update_user(
            user_id,
            last_query=command
        )


    # ==================================================
    # STATUS
    # ==================================================

    def change_status(self, user_id, status):

        return self.update_value(
            user_id,
            "status",
            status
        )


    def block_user(self, user_id):

        return self.change_status(
            user_id,
            "blocked"
        )


  

    def unblock_user(self, user_id):

        expiry = datetime.now() + timedelta(days=30)

        return self.update_user(
             user_id,
             status="active",
             expiry=expiry.strftime("%Y-%m-%d")
    )


            # ==================================================
            # NOTE
            # ==================================================

    def update_note(self, user_id, note):

        return self.update_value(
            user_id,
            "note",
            note
        )


    # ==================================================
    # EXPIRY
    # ==================================================

    def get_expiry(self, user_id):

        user = self.get_user(user_id)

        if not user:
            return None

        return datetime.strptime(
            user["expiry"],
            "%Y-%m-%d"
        )


    def is_expired(self, user_id):

       expiry = self.get_expiry(user_id)

       print("expiry =", expiry)
       print("now    =", datetime.now())

       if expiry is None:
        return True

       return datetime.now() > expiry

    def extend_days(self, user_id, days):

        expiry = self.get_expiry(user_id)

        if expiry is None:
            return False

        expiry += timedelta(days=days)

        return self.update_value(
            user_id,
            "expiry",
            expiry.strftime("%Y-%m-%d")
        )


    # ==================================================
    # STATISTICS
    # ==================================================

    def total_users(self):

        return len(self.users_cache)


    def active_users(self):

        return len([
            u for u in self.users_cache
            if u["status"] == "active"
        ])


    def trial_users(self):

        return len([
            u for u in self.users_cache
            if u["status"] == "trial"
        ])


    def block_user(self, user_id):

        return self.update_user(
            user_id,
            status="blocked"
        )

    def expired_users(self):

        count = 0

        for user in self.users_cache:

            try:

                expiry = datetime.strptime(
                    user["expiry"],
                    "%Y-%m-%d"
                )

                if expiry < datetime.now():

                    count += 1

            except:

                pass

        return count


    # ==================================================
    # SEARCH
    # ==================================================

    def search_user(self, keyword):

        keyword = str(keyword).lower()

        result = []

        for user in self.users_cache:

            if (
                keyword in str(user["user_id"]).lower()
                or keyword in user["name"].lower()
                or keyword in user["username"].lower()
            ):

                result.append(user)

        return result


    # ==================================================
    # LOG
    # ==================================================

    def write_log(self, user_id, command, result="OK"):

        self.logs_sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id,
            command,
            result
        ])


        # ==================================================
    # SUBSCRIPTION
    # ==================================================

    def is_trial(self, user_id):

        user = self.get_user(user_id)

        if not user:
            return False

        return user["status"] == "trial"


    def is_active(self, user_id):

        user = self.get_user(user_id)

        if not user:
            return False

        return user["status"] == "active"


    def is_blocked(self, user_id):

        user = self.get_user(user_id)

        if not user:
            return True

        return user["status"] == "blocked"

    def activate_user(self, user_id, days=30):

        expiry = datetime.now() + timedelta(days=days)

        return self.update_user(
            user_id,
            status="active",
            expiry=expiry.strftime("%Y-%m-%d")
        )



    def expire_user(self, user_id):

        return self.update_value(
            user_id,
            "status",
            "expired"
        )

    from datetime import datetime

    def can_use(self, user_id):

       user = self.get_user(user_id)

       print("========== DEBUG ==========")
       print(user)
       print("===========================")

       if not user:
        return False

    # Bị khóa
       if self.is_blocked(user_id):
        return False

    # Tài khoản dùng thử
       if user["status"] == "trial":

        if int(user["query_count"]) >= 10:
            return False

        return True

    # Tài khoản trả phí
       if self.is_expired(user_id):

        if user["status"] != "expired":
            self.expire_user(user_id)

        return False

       return True
    def days_left(self, user_id):

        expiry = self.get_expiry(user_id)

        if expiry is None:
            return 0

        delta = expiry - datetime.now()

        return max(delta.days, 0)


        # ==================================================
    # UPDATE USER (MULTI FIELD)
    # ==================================================

    def update_user(self, user_id, **kwargs):

        row = self.get_row(user_id)

        if not row:
           return False

        headers = self.users_sheet.row_values(1)

        uid = str(user_id)

        for column, value in kwargs.items():

            if column not in headers:
              continue

            col = headers.index(column) + 1

            self.users_sheet.update_cell(
                 row,
                 col,
                 value
        )

        # Cập nhật cache luôn
            if uid in self.user_cache:
               self.user_cache[uid][column] = value

        return True
    def blocked_users(self):

     return len([
        u for u in self.users_cache
        if u["status"] == "blocked"
    ])

sheet = GoogleSheet()