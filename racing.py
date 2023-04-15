import time
import tkinter
import random
import os
from PIL import Image, ImageTk

############################################################################### 
# 初期処理
############################################################################### 

# 仮想VRAMのサイズ
VRM_WIDTH = 32
VRM_HEIGHT = 24

# ゲームの状態
GAMESTATUS_TITLE = 0
GAMESTATUS_START = 1
GAMESTATUS_MAIN = 2
GAMESTATUS_MISS = 3
GAMESTATUS_OVER = 4

# 敵の最大数
ENEMY_MAX = 5

# ゲームの状態管理用
gameStatus = GAMESTATUS_TITLE

# ゲームの経過時間管理用
gameTime = 0

# キー判定用
KEY_LEFT = "Left"
KEY_RIGHT = "Right"
KEY_SPACE = "space"

# スクリプトのパス
basePath = os.path.abspath(os.path.dirname(__file__))

# 空の仮想VRAM配列
blankRow = [0] * VRM_WIDTH
vrm = [blankRow] * VRM_HEIGHT

# スクロール用のインデックスオフセット
indexOffset = 0

# 道幅
roadWidth = 12

# 道の横位置
roadX = 10

# プレイヤー座標
mx = 16
my = 20

# 敵キャラクタ
ex = [0] * ENEMY_MAX
ey = [0] * ENEMY_MAX
ev = [0] * ENEMY_MAX
es = [0] * ENEMY_MAX

# 敵の数
enemy_count = 0

# スコア
score = 0

# キー情報
key = ""
keyOff = False


############################################################################### 
# キー押す
############################################################################### 
def pressKey(e):
	global key, keyOff
	key = e.keysym
	keyOff = False


############################################################################### 
# キー離す
############################################################################### 
def releaseKey(e):
	global keyOff
	keyOff = True


############################################################################### 
# タイトル
############################################################################### 
def title():
	global gameStatus, gameTime, score, mx, my, roadWidth, roadX, enemy_count, vrm

	if key == KEY_SPACE:
		# スコア
		score = 0
		# プレイヤー座標
		mx = 16
		my = 20
		# 敵の初期化
		for i in range(0, ENEMY_MAX):
			es[i] = 0
		# 敵の数
		enemy_count = 0
		# 道幅
		roadWidth = 12
		# 道の横位置
		roadX = 10
		# バックグラウンド情報を初期化
		vrm = [blankRow] * VRM_HEIGHT
		# インデックスオフセット初期化
		indexOffset = 0
		# ゲーム開始
		gameStatus = GAMESTATUS_START
		gameTime = 0


############################################################################### 
# ゲームスタート
############################################################################### 
def gameStart():
	global gameStatus, gameTime
	
	# 道をだんだん表示する
	if gameTime < 24:
		generateRoad(False)

	if gameTime == 50:
		# ゲームメイン
		gameStatus = GAMESTATUS_MAIN
		gameTime = 0


############################################################################### 
# ゲームメイン
############################################################################### 
def gameMain():
	global score

	# 道を生成
	generateRoad()

	# プレイヤー移動
	movePlayer()

	# 敵
	moveEnemy()

	# スコア加算
	score = score + 1


############################################################################### 
# 道を生成
############################################################################### 
def generateRoad(isMove=True):
	global roadX, indexOffset

	if isMove == True:
		# 道路を左右に動かす
		v = random.randint(0, 2) - 1
		if (roadX + v > 0 and roadX + v < VRM_WIDTH - roadWidth - 1):
			roadX = roadX + v

	# 新しい表示行を生成
	newRow = [2] * VRM_WIDTH
	for w in range(roadWidth):
		newRow[roadX + w] = 0
	newRow[roadX - 1] = 1
	newRow[roadX + roadWidth] = 1

	# インデックスオフセット値を更新
	indexOffset -= 1
	if indexOffset < 0:
		indexOffset = VRM_HEIGHT - 1

	# 対象の仮想画面の行に生成した道を設定
	vrm[indexOffset] = newRow

############################################################################### 
# プレイヤー移動 & 衝突判定
############################################################################### 
def movePlayer():
	global gameStatus, gameTime, mx

	if key == KEY_LEFT and mx > 0:
		mx -= 1

	if key == KEY_RIGHT and mx < VRM_WIDTH:
		mx += 1

	# インデックスオフセットから当たり判定対象の仮想画面Y座標を算出
	ty = indexOffset + my
	if ty > VRM_HEIGHT - 1:
		ty = ty - VRM_HEIGHT

	# 当たり判定
	if vrm[ty][mx] > 0:
		# ミス
		gameStatus = GAMESTATUS_MISS
		gameTime = 0


############################################################################### 
# 敵の処理
############################################################################### 
def moveEnemy():
	global gameStatus, gameTime, enemy_count

	# 敵の数の変動
	if enemy_count < ENEMY_MAX and gameTime % 150 == 0:
		enemy_count += 1

	# 敵の出現・移動・衝突判定
	for e in range(enemy_count):
		# 敵が生きていれば移動
		if es[e] > 0:
			# esは1が直進、2が途中からプレイヤーに寄せてくる
			if es[e] == 2 and ey[e] < 15:
				if ex[e] > mx:
					ex[e] -= 1
				if ex[e] < mx:
					ex[e] += 1
			ey[e] = ey[e] + 1
			if ey[e] > 23:
				es[e] = 0
			if abs(ex[e] - mx) < 2 and abs(ey[e] - my) < 2:
				# ミス
				gameStatus = GAMESTATUS_MISS
				gameTime = 0

		# 敵が生きていなければ生成
		else:
			# 時間が100以下の時は出さない
			if gameTime > 100 and random.randint(0, 10) > 8:
				ex[e] = roadX + random.randint(0, roadWidth)
				ey[e] = 0
				ev[e] = 0
				es[e] = random.randint(1, 2)


############################################################################### 
# ミス
############################################################################### 
def miss():
	global gameStatus, gameTime

	if gameTime > 25:
		# ゲームオーバー
		gameStatus = GAMESTATUS_OVER
		gameTime = 0


############################################################################### 
# ゲームオーバー
############################################################################### 
def gameover():
	global gameStatus, gameTime

	if (gameTime > 10 and key == KEY_SPACE) or gameTime > 50:
		# タイトル
		gameStatus = GAMESTATUS_TITLE
		gameTime = 0


############################################################################### 
# 画面描画
############################################################################### 
def drawScreen():
	global gameTime

    # canvasのイメージ削除
	canvas.delete("TEXT1")
	canvas.delete("BG1")
	canvas.delete("PLAYER")
	canvas.delete("ENEMY")

	# バックグラウンド描画
	if gameStatus == GAMESTATUS_START or gameStatus == GAMESTATUS_MAIN or gameStatus == GAMESTATUS_MISS:
		# バックグラウンド描画
		for row in range(VRM_HEIGHT):
			vrow = row + indexOffset
			if vrow > VRM_HEIGHT - 1:
				vrow = vrow - VRM_HEIGHT
			for col in range(VRM_WIDTH):
				canvas.create_image(gPos(col), gPos(row), image = img_chr[vrm[vrow][col]], tag = "BG1")

    # キャラクタ描画
	if gameStatus == GAMESTATUS_MAIN:
		# プレイヤー
		canvas.create_image(gPos(mx), gPos(my), image = img_mycar, tag = "PLAYER")
		# 敵
		for e in range(enemy_count):
			if es[e] > 0:
				canvas.create_image(gPos(ex[e]), gPos(ey[e]), image = img_othercar, tag = "ENEMY")
	if gameStatus == GAMESTATUS_MISS:
		# プレイヤー
		canvas.create_image(gPos(mx), gPos(my), image = img_bang, tag = "PLAYER")

	# 文字描画
	if gameStatus == GAMESTATUS_TITLE:
		canvas.create_rectangle(0, 0, gPos(VRM_WIDTH), gPos(VRM_HEIGHT), fill = "Black")
		writeText(8, 6, "TINY RACING GAME", "TEXT1")
		writeText(2, 20, "PROGRAMMED BY ABURI6800 2020", "TEXT1")
		if gameTime < 25:
			writeText(9, 13, "PUSH SPACE KEY", "TEXT1")
		if gameTime == 50:
			gameTime = 0
	if gameStatus == GAMESTATUS_START:
		if gameTime > 30 and gameTime < 50:
			writeText(14, 13, "START", "TEXT1")
	if gameStatus == GAMESTATUS_OVER:
		writeText(12, 11, "GAME OVER", "TEXT1")

	writeText(0, 0, "SCORE " + "{:06}".format(score), "TEXT1")


############################################################################### 
# テキスト描画
# 引数		x テキスト座標系のx座標
#			y テキスト座標系のy座標
#			str 表示する文字列
#			tag canvasに指定するタグ
############################################################################### 
def writeText(x, y, str, tag="text1"):

	# 大文字に変換
	str = str.upper()

	# 文字を描画
	for i in range(len(str)):
		o = ord(str[i])
		if o >= 48 and o <= 57:
			canvas.create_image(gPos(x + i), gPos(y), image = img_font[o - 48], tag = tag)
		if o >= 65 and o <= 90:
			canvas.create_image(gPos(x + i), gPos(y), image = img_font[o - 55], tag = tag)


############################################################################### 
# 指定されたパスの画像をロードして2倍に拡大したImageを返却する
# 引数		filepath 画像データのフルパス
# 戻り値	2倍に拡大したImageデータ
############################################################################### 
def loadImage(filePath):

	img = Image.open(filePath).convert("RGBA")
	return img.resize((img.width * 2, img.height * 2), Image.NEAREST)


############################################################################### 
# テキスト座標系からグラフィック座標系に変換する
# 引数      value 変換する値
# 戻り値    変換後の値
############################################################################### 
def gPos(value):

	return value * 8 * 2 + 8


############################################################################### 
# メイン処理
############################################################################### 
def main():
	global gameTime, roadWidth, roadX, mx, key, keyOff

	# ゲームの経過時間を加算
	gameTime += 1

	# タイトル
	if gameStatus == GAMESTATUS_TITLE:
		title()

	# ゲームスタート
	if gameStatus == GAMESTATUS_START:
		gameStart()

	# ゲームメイン
	if gameStatus == GAMESTATUS_MAIN:
		gameMain()

	# ミス
	if gameStatus == GAMESTATUS_MISS:
		miss()

	# ゲームオーバー
	if gameStatus == GAMESTATUS_OVER:
		gameover()

	# 画面描画
	drawScreen()

	# キーリピート対策
	if keyOff == True:
		key = ""
		keyOff = False

	root.after(50, main)


# Windowを生成
root = tkinter.Tk()
root.geometry(str(gPos(VRM_WIDTH) - 8) + "x" + str(gPos(VRM_HEIGHT) - 8))
root.title("TintRacingGame")
root.bind("<KeyPress>", pressKey)
root.bind("<KeyRelease>", releaseKey)

# Canvas生成
canvas = tkinter.Canvas(width = gPos(VRM_WIDTH) - 8, height = gPos(VRM_HEIGHT) - 8)
canvas.pack()

# イメージをロード
img_mycar = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "mycar.png"))
img_othercar = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "othercar.png"))
img_bang = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "bang.png"))
img_chr = [
	ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "road.png")),
	ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "block.png")),
	ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "green.png"))
]

# フォントデータ
img_allfont = loadImage(basePath + os.sep + "Images" + os.sep + "font.png")
img_font = []
for w in range(0, img_allfont.width, 16):
	img = ImageTk.PhotoImage(img_allfont.crop((w , 0, w + 16, 16)))
	img_font.append(img)

# メイン処理
main()

# ウィンドウイベントループ実行
root.mainloop()
