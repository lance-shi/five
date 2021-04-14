import pygame
	
class Board:
	def __init__(self):
		self.screen = pygame.display.set_mode((1000, 820))
		self.background = pygame.image.load("res/board.jpg")
		gobanIcon = pygame.transform.scale(
			pygame.image.load("res/icon.png"), (20, 20))
		self.blackStone = pygame.transform.scale(
			pygame.image.load("res/black.png"), (38, 38))
		self.whiteStone = pygame.transform.scale(
			pygame.image.load("res/white.png"), (38, 38))
		pygame.display.set_caption("五子棋")
		pygame.display.set_icon(gobanIcon)
		pygame.mixer.init(44100, -16, 1, 512)
		pygame.font.init()
		self.winningFont = pygame.font.Font("font/sszz.ttf", 30)
		self.sounds = {}
		self.sounds["move"] = pygame.mixer.Sound("sound/move.wav")

		self.posX = 40
		self.posY = 40
		self.tileSize = 40
		self.htileSize = 20
		self.starSize = 5
		self.size = 19
		self.blackTurn = 1
		self.colors = {
			"BLACK": (0, 0, 0),
			"WHITE": (255, 255, 255),
			"RED": (255, 0, 0)
		}
		self.gameOver = False
		self.tiles = [[0 for i in range(self.size)] for i in range(self.size)]
		self.trace = [] # Record how the game is played

		self.restartText = self.winningFont.render("重新开始", True, self.colors["BLACK"])
		self.restartRect = self.restartText.get_rect(topleft=(860, 160))
		self.regretText = self.winningFont.render("撤回", True, self.colors["BLACK"])
		self.regretRect = self.regretText.get_rect(topleft=(860, 200))

		self.mainLoop()

	def mainLoop(self):
		clock = pygame.time.Clock()
		run = True

		while run:
			clock.tick(60)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					run = False
				if event.type == pygame.MOUSEBUTTONUP:
					if self.regretRect.collidepoint(event.pos):
						self.regret()
					if self.restartRect.collidepoint(event.pos):
						self.restart()
					elif not self.gameOver:
						self.getDown(event)

			self.screen.fill(self.colors["WHITE"])
			self.screen.blit(self.background, (0, 0))
			self.drawBoard()
			self.drawOptions()
			self.drawStars()
			self.drawStones()
			self.drawWinning()
			pygame.display.update()

		pygame.quit()

	def drawBoard(self):
		for x in range(0, self.size):
			for y in range(0, self.size):
				pygame.draw.line(self.screen, self.colors["BLACK"],
								 (self.posX + x * self.tileSize, self.posY + y * self.tileSize), (self.posX + x * self.tileSize, self.posY + y))
				pygame.draw.line(self.screen, self.colors["BLACK"],
								 (self.posX + x * self.tileSize, self.posY + y * self.tileSize), (self.posX + x, self.posY + y * self.tileSize))

	def drawStars(self):
		starLocation = [3, 9, 15]
		for x in starLocation:
			for y in starLocation:
				pos = (int(self.posX + x*self.tileSize), int(self.posY + y*self.tileSize))
				pygame.draw.circle(self.screen, self.colors["BLACK"], pos, self.starSize)

	def drawStones(self):
		for x in range(0, self.size):
			for y in range(0, self.size):
				if self.tiles[x][y] == 1:
					pos = (int(self.posX + x*self.tileSize) - 19, int(self.posY + y*self.tileSize) - 19)
					self.screen.blit(self.blackStone, pos)
				if self.tiles[x][y] == -1:
					pos = (int(self.posX + x*self.tileSize) - 19, int(self.posY + y*self.tileSize) - 19)
					self.screen.blit(self.whiteStone, pos)

	def getPos(self, pos):
		adjustX = pos[0] - self.posX + self.htileSize
		adjustY = pos[1] - self.posY + self.htileSize
		if adjustX >= 760 or adjustY >= 760:
			return (-1, -1)
		mouseX = int(adjustX / self.tileSize)
		mouseY = int(adjustY / self.tileSize)
		return (mouseX, mouseY)

	def getDown(self, event):
		x, y = self.getPos(event.dict['pos'])
		if x < 0 or y < 0:
			return
		if self.tiles[x][y] != 0:
			return
		else:
			self.tiles[x][y] = self.blackTurn
			self.trace.append([x, y, self.blackTurn])
			if self.judgeWinning(self.blackTurn, x, y):
				if self.blackTurn == 1:
					self.constructWinning("黑棋获胜")
				else:
					self.constructWinning("白棋获胜")
				self.gameOver = True
			else:
				self.blackTurn = -self.blackTurn
				self.sounds["move"].play()

	def constructWinning(self, winningParty):
		self.winningBoard = pygame.Surface((120, 40))
		self.winningBoard.set_colorkey((0,0,0))
		self.winningBoard.blit(self.winningFont.render(winningParty, False, self.colors["RED"]), [0, 0])
		self.winningBoardY = 820 + 40

	def drawWinning(self):
		if self.gameOver:
			if self.winningBoardY > 390: 
				self.winningBoardY -= 4
			self.screen.blit(self.winningBoard, [350, self.winningBoardY]) #378 = (820 - 64)/2

	def regret(self):
		if len(self.trace) == 0:
			return
		latest = self.trace.pop()
		self.tiles[latest[0]][latest[1]] = 0
		self.gameOver = False
		self.blackTurn = -self.blackTurn

	def restart(self):
		self.gameOver = False
		self.trace = []
		self.blackTurn = True
		for i in range(self.size):
			for j in range(self.size):
				self.tiles[i][j] = 0

	def drawOptions(self):
		self.screen.blit(self.restartText, self.restartRect)
		self.screen.blit(self.regretText, self.regretRect)
		self.screen.blit(self.winningFont.render("保存棋谱", True, self.colors["BLACK"]), [860, 240])
		self.screen.blit(self.winningFont.render("读取棋谱", True, self.colors["BLACK"]), [860, 280])

	def judgeWinning(self, curColor, x, y):
		verticalCount = 0
		for i in range(x-1, -1, -1):
			if self.tiles[i][y] == curColor:
				verticalCount += 1
				if verticalCount >= 4:
					return True
			else:
				break
		for i in range(x+1, self.size):
			if self.tiles[i][y] == curColor:
				verticalCount += 1
				if verticalCount >= 4:
					return True
			else:
				break

		horizontalCount = 0
		for i in range(y-1, -1, -1):
			if self.tiles[x][i] == curColor:
				horizontalCount += 1
				if horizontalCount >= 4:
					return True
			else:
				break
		for i in range(y+1, self.size):
			if self.tiles[x][i] == curColor:
				horizontalCount += 1
				if horizontalCount >= 4:
					return True
			else:
				break

		diagonalCount1 = 0
		for i in range(1, 5):
			if x - i >= 0 and y - i >=0 and self.tiles[x-i][y-i] == curColor:
				diagonalCount1 += 1
				if diagonalCount1 >= 4:
					return True
			else:
				break
		for i in range(1, 5):
			if x + i < self.size and y + i < self.size and self.tiles[x+i][y+i] == curColor:
				diagonalCount1 += 1
				if diagonalCount1 >= 4:
					return True
			else:
				break

		diagonalCount2 = 0
		for i in range(1, 5):
			if x - i >= 0 and y + i < self.size and self.tiles[x-i][y+i] == curColor:
				diagonalCount2 += 1
				if diagonalCount2 >= 4:
					return True
			else:
				break
		for i in range(1, 5):
			if x + i < self.size and y - i >= 0 and self.tiles[x+i][y-i] == curColor:
				diagonalCount2 += 1
				if diagonalCount2 >= 4:
					return True
			else:
				break

		return False

def main():
	game = Board()

if __name__ == '__main__':
	main()