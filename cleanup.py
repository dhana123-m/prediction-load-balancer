import os
import tempfile

def clean_temp():

    temp_dir = tempfile.gettempdir()

    removed = 0

    for file in os.listdir(temp_dir):
        path = os.path.join(temp_dir, file)

        try:
            if os.path.isfile(path):
                os.remove(path)
                removed += 1
        except:
            pass

    return f"{removed} temp files removed"