from Src.Num2Ques import *
from Src.CreateData import *
from Src.AdjustQues import *

with gr.Blocks() as demo:
    with gr.Tab("选错题"):
        with gr.Accordion("必看", open=False):
            gr.Markdown("""
                        1. 数据存放在{\.\./Data}，你可以先在根目录中输入，然后查看一级标题，看看有哪些可供选择的题库。再将题库的名字拼接到根目录即可。
                            目前可供选择的题库有：
                            + \.\./Data/数三880
                            + \.\./Data/数二880
                            + \.\./Data/数三1000
                        2. 可选择任意多个题目，每一张的每一小节选择好之后，点击添加按钮，然后选择其他章节，在右边可以看到选择的错题，全部选完之后点击生成
                        3. 下方有个可选择的题号，里面存放了你可以选择的题号，如果你的题号选择失误，你需要点击清空错题然后重新进行操作（所有错题放在了一个全局变量中，每次生成将会清除这个全局变量的内容）
                        4. 在右边你可以创建自己的题库，只需要上传一个错题本，因为一个题目可能对应很多页，可以到调整顺序哪里进行题目顺序的调整
                        5. 增添打印版选项，采用yolo8+微调精准分割图像，可自定义纸张(纸张类型可取网上查)，自定义题目之间的距离                     
                        """)
        with gr.Row():
            with gr.Column():
                path0 = gr.Textbox(label="请输入根目录:")

                path1 = gr.Dropdown([], label="一级标题")
                path0.change(show_listdir, inputs=path0, outputs=path1)

                path2 = gr.Dropdown([], label="二级标题")
                path1.change(show_listdir2, inputs=[path0, path1], outputs=path2)

                input_str = gr.Textbox(label="输入题号，并以空格隔开，题号不能超出")
                with gr.Row():
                    pdf_name = gr.Textbox(label="pdf的名字", value="1.pdf")
                    spacing = gr.Number(label="打印版题目之间的距离(打印版选择)", value=40, interactive=True)
                    page_size = gr.Textbox(label="纸张类型(打印版选择),本质张参考ISO 216 standard", value="A4", interactive=True)

                with gr.Row():
                    add_component = gr.Button(value="添加")
                    generate_conponent1 = gr.Button(value="生成错题本")
                    generate_conponent2 = gr.Button(value="生成打印本")
                    gr.Button(value="清空错题").click(clear_img_lists)

            with gr.Column():
                questions = gr.TextArea(label="选择的错题", interactive=False)
                output = gr.outputs.File(label="文件下载")
                add_component.click(add, inputs=[path0, path1, path2, input_str], outputs=questions)

                generate_conponent1.click(generate, inputs=[pdf_name], outputs=output)
                generate_conponent2.click(create_pdf_with_images, inputs=[spacing, pdf_name, page_size], outputs=output)

        with gr.Row():
            with gr.Accordion("查看可以选择的题号：", open=False):
                question_series = gr.Textbox(interactive=False)
                path2.change(show_question_series, inputs=[path0, path1, path2],
                             outputs=question_series)  # path2改变时将内容输入到question_series








    with gr.Tab("调整顺序"):
        with gr.Row():
            with gr.Column():
                path0 = gr.Textbox(label="请输入根目录:")

                path1 = gr.Dropdown([], label="一级标题")
                path0.change(show_listdir, inputs=path0, outputs=path1)

                path2 = gr.Dropdown([], label="二级标题")
                path1.change(show_listdir2, inputs=[path0, path1], outputs=path2)

                input_str = gr.Textbox(label="请输入调整的题号：")
                adjust = gr.Button(value="adjust")
                adjust.click(adjust_question, inputs=[path0, path1, path2, input_str], outputs=None)
            with gr.Column():
                question = gr.Textbox(label="请输入题号")
                text = gr.Image()






    with gr.Tab("创建数据"):
        WorkSpace = gr.Textbox(label="请确定工作区", value=r"../UserData", interactive=True)
        with gr.Row():
            with gr.Column():
                file = gr.File()
            with gr.Column():
                dpi = gr.Number(label="图片清晰度，越高越慢", value=300, precision=0)  # 转换为int
                flip = gr.Radio(choices=["yes", "no"], label="是否需要裁剪图片", interactive=False, )  # 是否需要裁剪图片
                height = gr.Number(label="裁剪高度", interactive=False)
        with gr.Accordion(label="目录查看", open=False):
            Outline = gr.TextArea(label="生成的目录", interactive=False, layout={"width": 200, "height": 100})

        with gr.Row():
            Generate_Outline = gr.Button(value="生成目录")
            Local_Outline = gr.Button(value="本地目录创建")
            Save_Pic = gr.Button(value="数据保存")
        Local_Outline.click(create_directory_structure, inputs=[file, WorkSpace], outputs=None)
        Generate_Outline.click(show_outline, inputs=file, outputs=Outline)
        Save_Pic.click(extract_pdf_images, inputs=[file, WorkSpace, dpi], outputs=None)

demo.launch(share=False)