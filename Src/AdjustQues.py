import gradio as gr
import os

# 调整题号
def renames(source,target,root_path):
    for k,v in zip(source,target):
        if os.path.exists(fr"{root_path}\{k}"):
            os.rename(fr"{root_path}\{k}",fr"{root_path}\{v}")


def adjust_question_(start, length,filename):
    index = filename.index(f"{start}.png")
    left_list = filename[:index]
    need_change = [f"{start}.{i}.png" for i in range(1, length+1)]
    right_list = filename[index+1:index+1+len(filename)-len(left_list)-length]
    return left_list + need_change + right_list

def adjust_question(path0,path1,path2,input_str):
    path1 = os.path.join(path0,path1)
    root_path = os.path.join(path1,path2)
    root_path_pic = os.listdir(root_path)
    filenames = sorted(root_path_pic, key=lambda x: int(x.split('.')[0]) if x.split('.')[0].isdigit() else float('inf'))
    modified_filenames = filenames.copy()
    for item in input_str.split():
        start, length = map(int, item.split(','))
        modified_filenames = adjust_question_(start,length,modified_filenames)
    renames(filenames,modified_filenames,root_path)
