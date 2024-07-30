import json


class StorageManager:
    def load_data(self, data_name):
        filename = self.get_filename(data_name)
        try:
            file = open(filename, "r")
            data = file.read()
            file.close()
        except:
            return None
        return json.loads(data)

    def save_data(self, data_name, data_content):
        filename = self.get_filename(data_name)
        data_str = json.dumps(data_content, indent=4)
        file = open(filename, "w")
        file.write(data_str)
        file.close()

    @staticmethod
    def get_filename(data_name):
        return "./jsons/" + data_name + ".json"
