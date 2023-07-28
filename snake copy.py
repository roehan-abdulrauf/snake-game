import tkinter as tk
import random

class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Jeu du Serpent")

        self.canvas_width = 400
        self.canvas_height = 400

        self.canvas = tk.Canvas(self.window, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()

        self.player_name = tk.StringVar()
        self.name_label = tk.Label(self.window, text="Nom du joueur:")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.window, textvariable=self.player_name)
        self.name_entry.pack()

        self.start_button = tk.Button(self.window, text="Démarrer", command=self.start_game)
        self.start_button.pack()

        self.score_label = tk.Label(self.window, text="Scores précédents:")
        self.score_label.pack()

        self.score_text = tk.Text(self.window, width=30, height=10)
        self.score_text.pack()

        self.scores = []

    def start_game(self):
        player_name = self.player_name.get()
        if player_name:
            self.clear_canvas()
            self.canvas.focus_set()
            self.canvas.bind("<KeyPress>", self.handle_keypress)

            self.snake_direction = "Right"
            self.snake_segments = [(80, 100), (60, 100), (40, 100)]
            self.food_position = self.generate_food()

            self.score = 0
            self.score_label.config(text="Score: {}".format(self.score))

            self.game_loop()
        else:
            tk.messagebox.showinfo("Erreur", "Veuillez entrer un nom de joueur.")

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_segment(self, position):
        x, y = position
        self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="white")

    def draw_snake(self):
        for segment in self.snake_segments:
            self.draw_segment(segment)

    def draw_food(self):
        self.draw_segment(self.food_position)

    def generate_food(self):
        x = random.randint(1, (self.canvas_width - 20) // 20) * 20
        y = random.randint(1, (self.canvas_height - 20) // 20) * 20
        return x, y

    def handle_keypress(self, event):
        key = event.keysym
        directions = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}

        if key in directions and directions[key] != self.snake_direction:
            self.snake_direction = key

    def move_snake(self):
        head_x, head_y = self.snake_segments[0]

        if self.snake_direction == "Up":
            new_segment = (head_x, head_y - 20)
        elif self.snake_direction == "Down":
            new_segment = (head_x, head_y + 20)
        elif self.snake_direction == "Left":
            new_segment = (head_x - 20, head_y)
        else:
            new_segment = (head_x + 20, head_y)

        self.snake_segments = [new_segment] + self.snake_segments[:-1]

    def check_collision(self):
        head = self.snake_segments[0]
        x, y = head

        # Vérifier la collision avec les bords du canevas
        if x < 0 or x >= self.canvas_width or y < 0 or y >= self.canvas_height:
            return True

        # Vérifier la collision avec le corps du serpent
        if head in self.snake_segments[1:]:
            return True

        return False

    def check_food_collision(self):
        if self.snake_segments[0] == self.food_position:
            return True

        return False

    def update_score(self):
        self.score += 1
        self.score_label.config(text="Score: {}".format(self.score))

    def game_over(self):
        player_name = self.player_name.get()
        score_entry = "{} - {}\n".format(player_name, self.score)
        self.scores.append(score_entry)

        self.score_text.insert(tk.END, score_entry)
        self.score_text.see(tk.END)

        self.canvas.unbind("<KeyPress>")
        self.start_button.config(text="Rejouer", command=self.start_game)

    def game_loop(self):
        if self.check_collision():
            self.game_over()
            return

        self.clear_canvas()
        self.move_snake()
        self.draw_snake()
        self.draw_food()

        if self.check_food_collision():
            self.update_score()
            self.food_position = self.generate_food()

        self.window.after(200, self.game_loop)

if __name__ == "__main__":
    game = SnakeGame()
    game.window.mainloop()



#  version avec pygame

# import tkinter as tk
import tkinter as tk
import pygame
import pymysql
import time
import random

class SnakeGame:
    def __init__(self):
        self.db_host = "localhost"
        self.db_user = "root"
        self.db_password = "root"
        self.db_name = "snake_game"
        self.window = tk.Tk()
        self.window.title("Jeu du Serpent")

        self.canvas_width = 400
        self.canvas_height = 400

        self.canvas = tk.Canvas(self.window, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack()

        self.player_name = tk.StringVar()
        self.name_label = tk.Label(self.window, text="Nom du joueur:")
        self.name_label.pack()

        self.name_entry = tk.Entry(self.window, textvariable=self.player_name)
        self.name_entry.pack()

        self.start_button = tk.Button(self.window, text="Démarrer", command=self.start_game)
        self.start_button.pack()

        self.score_label = tk.Label(self.window, text="Scores précédents:")
        self.score_label.pack()

        self.score_text = tk.Text(self.window, width=30, height=10)
        self.score_text.pack()

        self.scores = self.retrieve_scores_from_db()
        self.update_score_text()

        self.taille_serpent = 3

    def start_game(self):
        player_name = self.player_name.get()
        if player_name:
            self.clear_canvas()
            self.canvas.focus_set()
            self.canvas.bind("<KeyPress>", self.handle_keypress)

            self.snake_direction = "Right"
            self.snake_segments = [(80, 100), (60, 100), (40, 100)]
            self.food_position = self.generate_food()

            self.score = 0
            self.score_label.config(text="Score: {}".format(self.score))

            self.start_time = time.time()  # Enregistrer le moment où le jeu commence
            
            self.game_loop()
        else:
            tk.messagebox.showinfo("Erreur", "Veuillez entrer un nom de joueur.")

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_segment(self, position):
        x, y = position
        self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="white")

    def draw_snake(self):
        for segment in self.snake_segments:
            self.draw_segment(segment)

    def draw_food(self):
        self.draw_segment(self.food_position)

    def generate_food(self):
        x = random.randint(1, (self.canvas_width - 20) // 20) * 20
        y = random.randint(1, (self.canvas_height - 20) // 20) * 20
        return x, y

    def handle_keypress(self, event):
        key = event.keysym
        directions = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}

        if key in directions and directions[key] != self.snake_direction:
            self.snake_direction = key

    def move_snake(self):
        head_x, head_y = self.snake_segments[0]

        if self.snake_direction == "Up":
            new_segment = (head_x, head_y - 20)
        elif self.snake_direction == "Down":
            new_segment = (head_x, head_y + 20)
        elif self.snake_direction == "Left":
            new_segment = (head_x - 20, head_y)
        else:
            new_segment = (head_x + 20, head_y)

        self.snake_segments = [new_segment] + self.snake_segments[:-1]

    def check_collision(self):
        head = self.snake_segments[0]
        x, y = head

        if x < 0 or x >= self.canvas_width or y < 0 or y >= self.canvas_height:
            return True

        if head in self.snake_segments[1:]:
            return True

        return False

    def check_food_collision(self):
        if self.snake_segments[0] == self.food_position:
            self.snake_segments.append((0, 0))
            self.food_position = self.generate_food()
            self.update_score()
            return True

        return False

    def update_score(self):
        self.score += 1
        self.taille_serpent += 1
        self.score_label.config(text="Score: {}".format(self.score))

    def retrieve_scores_from_db(self):
        scores = []

        db = pymysql.connect(host=self.db_host, user=self.db_user, passwd=self.db_password, db=self.db_name)
        cursor = db.cursor()

        query = "SELECT joueur, score FROM scores ORDER BY score DESC"
        cursor.execute(query)

        for row in cursor:
            player_name = row[0]
            score = row[1]
            scores.append((player_name, score))

        cursor.close()
        db.close()

        return scores

    def send_score_to_db(self):
        db = pymysql.connect(host=self.db_host, user=self.db_user, passwd=self.db_password, db=self.db_name)
        cursor = db.cursor()
        cursor.execute("INSERT INTO scores (joueur, score) VALUES (%s, %s)", (self.player_name.get(), self.score))
        db.commit()
        db.close()
        self.update_score_text()  # Mettre à jour le canvas des scores avec le nouveau score ajouté

    def play_game_over_music(self):
        pygame.mixer.init()
        pygame.mixer.music.load("GameOver.wav")
        pygame.mixer.music.play()

    def game_over(self):
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_text = "Temps écoulé: {} min {} sec".format(minutes, seconds)
        self.score_label.config(text="Game Over", fg="red")
        self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2, text="Game Over", fill="red", font=("Arial", 24))
        self.canvas.create_text(self.canvas_width / 2, self.canvas_height / 2 + 30, text=time_text, fill="white", font=("Arial", 16))
        self.play_game_over_music()

        player_name = self.player_name.get()
        score_entry = "{} - {}\n".format(player_name, self.score)
        self.scores.append(score_entry)

        self.update_score_text()
        self.canvas.unbind("<KeyPress>")
        self.start_button.config(text="Rejouer", command=self.start_game)
        self.send_score_to_db()

    def game_loop(self):
        if self.check_collision():
            self.game_over()
            return

        self.clear_canvas()
        self.move_snake()
        self.draw_snake()
        self.draw_food()

        if self.check_food_collision():
            self.update_score()
            self.food_position = self.generate_food()

        self.window.after(200, self.game_loop)

    def update_score_text(self):
        self.score_text.delete("1.0", tk.END)  # Efface le contenu existant du canvas des scores
        for score in self.scores:
            joueur, score = score
            score_entry = "{} - {}\n".format(joueur, score)
            self.score_text.insert(tk.END, score_entry)

if __name__ == "__main__":
    game = SnakeGame()
    game.window.mainloop()
