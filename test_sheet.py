from google_sheet import GoogleSheet

sheet = GoogleSheet()

sheet.register_user(
    1555474257,
    "Tram Nguyen",
    "tram"
)

print(sheet.get_user(1555474257))