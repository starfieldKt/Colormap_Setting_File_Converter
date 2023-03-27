# xml.etree.ElementTreeをETとしてインポート、ファイル選択のためのライブラリ、ファイルパスのためのos.pathをインポート
import xml.etree.ElementTree as ET
from tkinter import filedialog
import os.path

# ファイル選択ダイアログで開くファイル形式の指定
typ = [("XMLファイル", "*.xml")]
# ホームディレクトリを取得
dir = os.path.expanduser("~")
# ファイル選択ダイアログを開いてファイルパスを取得
file = filedialog.askopenfilename(filetypes=typ, initialdir=dir)

if not file:
    exit()

# 選択したファイルをETで解析してroot要素を取得
tree_qgis = ET.parse(file)
root_qgis = tree_qgis.getroot()

# テンプレートファイル名
template_filename = "template.cmsetting"

# テンプレートファイルを読み込み
tree_template = ET.parse(template_filename)
root_template = tree_template.getroot()

# tree_qgis要素内のすべてのcolorramp要素を取得
for colorramp in tree_qgis.findall(".//colorramp"):
    # colorramp要素のname属性を取得して変数nameに代入
    name = colorramp.get("name")

    # stopsオプションから、各カラーストップを取得して、リストに格納
    option = colorramp.find(".//Option[@name='stops']")

    if option is None:
        stops_str = ""
        stops = []
    else:
        stops_str = option.attrib["value"]
        # stops_strを分割してstopsリストに格納
        stops = [
            [float(stop.split(";")[0])] + list(map(int, stop.split(";")[1].split(",")))
            for stop in stops_str.split(":")
        ]

    # color1オプションから、最初の色を取得して、リストに格納
    color1_str = colorramp.find(".//Option[@name='color1']").attrib["value"]
    color1 = [0.0] + list(map(int, color1_str.split(",")))[:-1]

    # color2オプションから、最後の色を取得して、リストに格納
    color2_str = colorramp.find(".//Option[@name='color2']").attrib["value"]
    color2 = [1.0] + list(map(int, color2_str.split(",")))[:-1]

    # color1, stops, color2を合成したカラーリストを作成
    result = [color1] + stops + [color2]

    # テンプレートの既存のItem要素を削除
    for item in root_template.findall(".//Item"):
        root_template.remove(item)

    # 新たなItem要素を作成
    for i in range(len(result)):
        value = result[i][0]
        rgb = result[i][1:]
        color = "#{:02x}{:02x}{:02x}".format(*rgb)
        item = ET.Element("Item")
        item.set("value", str(value))
        item.set("color", color)
        item.set("transparent", "false")
        root_template.append(item)

    # ファイル出力
    new_filename = name + ".cmsetting"
    tree_template.write(new_filename, encoding="utf-8", xml_declaration=True)
