# import os
# import datetime
# import shutil

# base_name = os.path.dirname(os.path.realpath(__file__))
# tmp_folder_name = "tmp-%s"%datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
# db_folder = os.path.join(base_name, "..", "data", tmp_folder_name)
# if not os.path.exists(db_folder):
#     os.makedirs(db_folder)
    

# zip_file_name = "project_%s_%s"%(projectid,  datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
# shutil.make_archive(os.path.join(base_name, "..", "data", zip_file_name), 'zip', db_folder)