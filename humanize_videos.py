import os, sys, re, datetime, shutil


def get_script_date():
    script_date = None
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if re.match(r'\d{2}.\d{2}.\d{2,4}', arg):
                script_date = arg
                day, month, year = script_date.split('.')
                script_date = datetime.datetime.strptime(month + '-' + day + '-' + year, '%m-%d-%Y')
    if len(sys.argv) == 1:
        yesterday = datetime.datetime.today() - datetime.timedelta(hours=24)
        yesterday = str(yesterday).split(' ')[0]
        yesterday = datetime.datetime.strptime(yesterday, '%Y-%m-%d')
        return yesterday

    return script_date


def go_to_folder_with_cams():
    folder_with_cameras = None
    for item in os.listdir():
        if len(item.split('.')) == 1:
            folder_with_cameras = item
    os.chdir(folder_with_cameras)


def get_xiaomi_date(folder_name):
    try:
        folder_name = folder_name[:8]
        xiaomi_date = datetime.datetime.strptime(folder_name[4:6] + '-' + folder_name[6:] + '-' + folder_name[:4], '%m-%d-%Y')
    except Exception:
        xiaomi_date = None
    return xiaomi_date


def convert_video_to_one_file(video_folder_dir):
    try:
        os.chdir(video_folder_dir)
        file_to_write = video_folder_dir + '/' + video_folder_dir.split('/')[-1] + '.mkv'
        if len(os.listdir()) > 1:
            video_files = os.listdir()
            f_list = save_flist(video_files)
            call = f'ffmpeg -f concat -safe 0 -i {f_list} -c copy {file_to_write} -y'
            os.system(call)
            os.remove(f_list)

            return video_files
    except Exception as err:
        print('data folder -->', data_folder)
        print('convert_video_to_one_file_err -->', err)
        return None


def remove_xiaomi_videos(video_files):
    try:
        for file in video_files:
            os.remove(file)
    except Exception as err:
        print('remove_video_error -->', err)


def creating_new_dirs(camera_folder_dir, script_date):
    os.chdir(camera_folder_dir)
    new_folders = []
    for data_folder in os.listdir():
        df = data_folder[:8]
        if script_date:
            xiaomi_date = get_xiaomi_date(data_folder)
            if xiaomi_date:
                if xiaomi_date <= script_date:
                    folder_name = df[6:] + '_' + df[4:6] + '_' + df[:4]  # day_month_year
                    new_folders.append(folder_name)
        else:
            folder_name = df[6:] + '_' + df[4:6] + '_' + df[:4]  # day_month_year
            new_folders.append(folder_name)

    new_folders = list(set(new_folders))

    for folder in new_folders:
        try:
            os.mkdir(folder)
        except Exception:
            print('folder --> ', folder, '  exist')



def shutil_move(data_folder):
    df = data_folder[:8]

    folder_name = df[6:] + '_' + df[4:6] + '_' + df[:4]
    folder_to_move = [folder for folder in os.listdir() if re.match(folder_name, folder)][0]
    os.chdir(data_folder)
    for file in os.listdir():
        file_full_path = camera_folder_dir + '/' + data_folder + '/' + file
        new_destination_full_path = camera_folder_dir + '/' + folder_to_move + '/' + file
        shutil.move(file_full_path, new_destination_full_path)


def moving_videos(camera_folder_dir, script_date):
    for data_folder in os.listdir():
        os.chdir(camera_folder_dir)

        if re.search('_', data_folder) is None:
            if script_date:
                xiaomi_date = get_xiaomi_date(data_folder)
                if xiaomi_date:
                    if xiaomi_date <= script_date:
                        shutil_move(data_folder)
            else:
                shutil_move(data_folder)


def delete_empty_folders(camera_folder_dir):
    os.chdir(camera_folder_dir)
    folder_to_delete = [folder for folder in os.listdir() if len(os.listdir(camera_folder_dir + '/' + folder)) == 0]
    try:
        for folder in folder_to_delete:
            os.rmdir(folder)
    except Exception as err:
        print('delete_empty_directory_err -->', err)


def save_flist(files):
    f_data = 'file \'' + '\'\nfile \''.join(files) + '\''

    f_list = 'list.txt'
    with open(f_list, 'w', encoding='gbk') as f:
        f.write(f_data)
    return f_list


if __name__ == '__main__':
    script_date = get_script_date()
    print(script_date)

    go_to_folder_with_cams()

    base_dir = os.getcwd()

    # part 1 concatenate videos in one file and delete old files
    for camera_folder in os.listdir():
        camera_folder_dir = base_dir + '/' + camera_folder
        os.chdir(camera_folder_dir)
        for data_folder in os.listdir():
            print('data folder -->', data_folder)
            video_folder_dir = camera_folder_dir + '/' + data_folder

            if script_date:
                xiaomi_date = get_xiaomi_date(data_folder)
                if xiaomi_date:
                    if xiaomi_date <= script_date:
                        video_files = convert_video_to_one_file(video_folder_dir)
                        if video_files:
                            remove_xiaomi_videos(video_files)
            else:
                if re.search(r'\d{2}_\d{2}_\d{2,4}', video_folder_dir) is None:
                    video_files = convert_video_to_one_file(video_folder_dir)

                    if video_files:
                        remove_xiaomi_videos(video_files)

        # part 2 creating new dirs
        creating_new_dirs(camera_folder_dir, script_date)

        # part 3 moving video from xiaomi folders to knew folders
        moving_videos(camera_folder_dir, script_date)

        # pert 4 delete empty folders
        delete_empty_folders(camera_folder_dir)


