

# Importing necessary libraries for handling CSV files, dates, random selections, and system operations
# Standard libraries
import csv
import datetime
import os
import random
import statistics
import sys
from abc import ABC, abstractmethod
from datetime import datetime

# GUI libraries
import tkinter as tk
from tkinter import Canvas, Frame, Label, Scrollbar, Tk, messagebox, simpledialog, ttk

# External libraries
import cv2
import pygame
from PIL import Image, ImageTk




class VideoPlayer(tk.Toplevel):
    def __init__(self, parent, video_path):
        super().__init__(parent)
        # Inicializa a captura de vídeo usando OpenCV.
        self.video = cv2.VideoCapture(video_path)
        # Se o vídeo não puder ser aberto, exibe um erro e encerra a janela.
        if not self.video.isOpened():
            print(f"Erro ao carregar o vídeo: {video_path}")
            self.destroy()
            return

        # Configura a janela para ficar no topo e inicia maximizada.
        self.attributes('-topmost', True)
        self.state('zoomed')

        # Cria um label para exibir cada frame do vídeo.
        self.label = tk.Label(self)
        self.label.pack()
        # Inicializa a variável que armazenará a referência da imagem.
        self.photo = None
        # Inicia o processo de atualização de frames do vídeo.
        self.update_frame()

    def update_frame(self):
        # Lê o próximo frame do vídeo.
        ret, frame = self.video.read()
        # Se houver um frame, atualiza a imagem no label.
        if ret:
            # Converte o frame para o formato de cor apropriado.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Cria um objeto PhotoImage com o frame.
            image = Image.fromarray(frame)
            self.photo = ImageTk.PhotoImage(image=image)
            # Atualiza o label com a nova imagem.
            self.label.config(image=self.photo)
            # Aguarda antes de atualizar o próximo frame.
            self.after(33, self.update_frame)
        else:
            # Se não houver mais frames, libera o vídeo e fecha a janela.
            print("Fim do vídeo ou erro de leitura.")
            self.video.release()
            self.destroy()

def play_video():
    global video_window  # Declara que video_window é uma variável global.
    # Tenta fechar a janela de vídeo anterior, se houver.
    try:
        video_window.destroy()
    except Exception as e:
        # Se não houver janela anterior, ignora o erro.
        print(f"Nenhuma janela anterior para fechar: {e}")
    
    # Cria uma nova janela para exibir o vídeo e a define como ativa.
    video_window = VideoPlayer(None, "logos/golos.mp4")
    video_window.grab_set()

# Inicializa o mixer do Pygame para manipulação de áudio.
pygame.mixer.init()

# Carrega e reproduz uma música de fundo em loop.
pygame.mixer.music.load('logos/champions.mp3')
pygame.mixer.music.play(-1)  # -1 faz com que a música toque em loop infinito.

# Definição de variáveis globais. Tenho noção que em termos de programação por objectos não é aconselhável a existência de tantas VG. 
#explicação dada no relatório final 
username = None
chosen_team = None
mix = False
players_list = None
global user_selected_player  # Declaração de variável global.
image_references = []
window_is_alive = True
global player1, player2, player_selection_count  # Declaração de múltiplas variáveis globais.
player1 = None
player2 = None
player_selection_count = 0

def update_image(label, gif_path, frame_number, size):
    # Atualiza a imagem de um label com frames de um GIF.
    try:
        image = Image.open(gif_path)
        image.seek(frame_number)
        image = image.resize(size)
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo
        label.after(100, update_image, label, gif_path, frame_number + 1, size)
    except EOFError:
        # Quando o GIF chega ao fim, reinicia a animação.
        update_image(label, gif_path, 0, size)

def show_gifs(result):
    # Exibe GIFs com base no resultado de um jogo ou evento.
    if tk._default_root:
        # Destrói a raiz Tkinter anterior, se existir.
        tk._default_root.destroy()

    gif_size = (300, 300)

    # Cria uma nova janela Tkinter para exibir os GIFs.
    records_window = tk.Tk()
    records_window.title("Congratulations")

    # Escolhe GIFs baseados no resultado fornecido.
    if result == 1:
        left_gif_path = "logos/dicaprio.gif"
        right_gif_path = "logos/si.gif"
    else:
        left_gif_path = "logos/looser.gif"
        right_gif_path = "logos/looser2.gif"

    # Configura e exibe os GIFs e mensagens correspondentes.
    left_label = tk.Label(records_window)
    left_label.grid(row=0, column=0, padx=10, pady=10)
    update_image(left_label, left_gif_path, 0, gif_size)

    right_label = tk.Label(records_window)
    right_label.grid(row=0, column=2, padx=10, pady=10)
    update_image(right_label, right_gif_path, 0, gif_size)

    msg_frame = tk.Frame(records_window)
    msg_frame.grid(row=0, column=1, padx=10, pady=10)

    # Exibe mensagens personalizadas com base no resultado.
    if result == 1:
        tk.Label(msg_frame, text="Congrats.", font=("Arial", 24)).pack()
        tk.Label(msg_frame, text="You guessed the opponent's player!", font=("Arial", 24)).pack()
        tk.Label(msg_frame, text="You win!", font=("Arial", 24)).pack()
    else:
        tk.Label(msg_frame, text="Ups!", font=("Arial", 24)).pack()
        tk.Label(msg_frame, text="The opponent guessed your player", font=("Arial", 24)).pack()
        tk.Label(msg_frame, text="Best luck next time!", font=("Arial", 24)).pack()

    records_window.mainloop()

def on_close():
    global window_is_alive
    if window_is_alive:
        print("Closing the program...")
        #root.destroy()
        sys.exit()
        #window_is_alive = False  # Indica que a janela foi destruída
    
        
        




  
class CSVOperation(ABC):
    
    
    @abstractmethod
    def read_csv(self, filename):
        """ Método abstrato para ler um arquivo CSV. """
        pass

    @abstractmethod
    def write_csv(self, data, filename):
        """ Método abstrato para escrever em um arquivo CSV. """
        pass
    
# Class to handle user verification and greetings
class UserChecker(CSVOperation):
    
    def __init__(self, filename='users.csv'):
        self._filename = filename  # Private attribute to hold the filename
        self.username = username
  
    # Property decorator for filename attribute
    @property
    def filename(self):
        return self._filename

    # Setter method for filename property
    @filename.setter
    def filename(self, value):
        self._filename = value

    # Method to check if a user exists in the CSV file
    def read_csv(self, filename):
        try:
            with open(filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                return [row for row in csv_reader]
        except FileNotFoundError:
            print(f"File not found: {filename}")
            return []
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []

    def write_csv(self, data, filename):
        try:
            with open(filename, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(data)
        except IOError:
            print(f"Error writing to file: {filename}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def check_user(self, username):
        users = self.read_csv(self._filename)
        return any(username in user for user in users)

class UserGreeter(UserChecker):
    def greet_user(self, username):
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal

        if self.check_user(username):
            messagebox.showinfo("Greeting", f"Welcome back, {username}!")
            root.state('zoomed')
        else:
            messagebox.showinfo("Greeting", f"Welcome, {username}!")
            root.state('zoomed')
            self.add_user(username)
 # Certifique-se de que esta função esteja definida ou mova para esta classe
        root.destroy()


    def add_user(self, username):
        self.write_csv([username], self._filename)
    # Method to handle team selection for the user
  
  
def update_chosen_team(team, root, players_list):
    global chosen_team
    global mix
    chosen_team = team
    messagebox.showinfo("Team Selected", f"You have selected {team}")

    if team == "mix mode":
        mix=True
        chosen_team_player = None
        chosen_team_computer = None
        game_instance = TypeOfGame(all_players=players_list)
        game_instance.start_game(root,chosen_team_player, chosen_team_computer)
    else:
        teams = ["Sporting", "Benfica", "Porto"]
        chosen_team_computer = random.choice(teams)
        messagebox.showinfo("Computer's Choice", f"The opponent selected {chosen_team_computer}")
        
        game_instance = TypeOfGame(all_players=players_list)
        game_instance.start_game(root,chosen_team, chosen_team_computer)

    # Fechar a janela atual após a escolha
    root.destroy()

def select_team(root,players_list):
    root.destroy()
    root = tk.Tk()
    root.title("Select Team")

    # Centraliza e maximiza a janela
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH)

    choose_team_label = tk.Label(frame, text="Choose Team", font=("Arial", 18))
    choose_team_label.pack(pady=(50, 10))

    team_frame = tk.Frame(frame)
    team_frame.pack(expand=True)

    teams = {
        "Sporting": "logos/scp.png",
        "Benfica": "logos/slb.png",
        "Porto": "logos/fcp.png",
        "mix mode": "logos/random.png"
    }

    for team, logo_path in teams.items():
        try:
            img = Image.open(logo_path)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            # Agora passando root e players_list para update_chosen_team
            btn = tk.Button(team_frame, image=photo, command=lambda t=team: update_chosen_team(t, root, players_list))
            btn.image = photo
            btn.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error loading image {logo_path}: {e}")

    btn_main_menu = tk.Button(root, text="Main Menu", command=lambda: display_menu(players_list), height=1, width=15)
    btn_main_menu.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

# Supondo que exista uma função display_menu() que você queira chamar após a seleção da equipe
# def display_menu(players_list):
#     # Sua lógica para exibir o menu principal aqui

# Class to handle player attributes and methods

class Player():
    def __init__(self, name, team_name, hair_color, hair_length, skin_color, continent, goals, assists, position):
        # Initializing player attributes
        self._name = name
        self._team_name = team_name
        self._hair_color = hair_color
        self._hair_length = hair_length
        self._skin_color = skin_color
        self._continent = continent
        self._goals = goals
        self._assists = assists
        self._position = position
       
    coach_players = []
 

    
    # Method to calculate median of goals and assists
    def calculate_goals_and_assists_median(self, players):
        goals = [player.goals for player in players]
        assists = [player.assists for player in players]
        goals_median = statistics.median(goals)
        assists_median = statistics.median(assists)
        return goals_median, assists_median
    
    

   

    
    def add_goals(self, amount):
        if isinstance(amount, int):
            self.goals += amount
        return self
    
    def add_assists(self, amount):
        if isinstance(amount, int):
            self.assists += amount
        return self
    
    def __iadd__(self, other):
        if isinstance(other, int): 
           
            if "goals" in self.__dict__:
                self.add_goals(other)
            elif "assists" in self.__dict__:
                self.add_assists(other)
        return self

    def __add__(self, other):
        total_goals = self.goals + other.goals
        total_assists = self.assists + other.assists
        return Player("Combined Players", total_goals, total_assists)
    
    # Property decorators and setters for player attributes
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def team_name(self):
        return self._team_name

    @team_name.setter
    def team_name(self, value):
        self._team_name = value

    @property
    def hair_color(self):
        return self._hair_color

    @hair_color.setter
    def hair_color(self, value):
        self._hair_color = value

    @property
    def hair_length(self):
        return self._hair_length

    @hair_length.setter
    def hair_length(self, value):
        self._hair_length = value

    @property
    def skin_color(self):
        return self._skin_color

    @skin_color.setter
    def skin_color(self, value):
        self._skin_color = value

    @property
    def continent(self):
        return self._continent

    @continent.setter
    def continent(self, value):
        self._continent = value

    @property
    def goals(self):
        return self._goals

    @goals.setter
    def goals(self, value):
        self._goals = value

    @property
    def assists(self):
        return self._assists

    @assists.setter
    def assists(self, value):
        self._assists = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value.rstrip(';')

    # Class method to load players from a CSV file
    @classmethod
    def load_players_from_csv(self, filename='players.csv'):
        global players_list 
        players_list = []
       
        try:
            with open(filename, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    row = [field.strip() for field in row]
                    row[-1] = row[-1].rstrip(';')
                    name, team, hair_color, hair_length, skin_color, continent, goals, assists, position = row
                    player = self(name, team, hair_color, hair_length, skin_color, continent, int(goals), int(assists), position)
                    players_list.append(player)
            #print("Carregamento de jogadores com sucesso!")        
            return players_list
        except Exception as e:
            print(f"Error loading players from CSV: {e}")
            return []

    

class Coach:
    def __init__(self, name, years_of_experience, titles):
        self.name = name
        self.years_of_experience = years_of_experience
        self.titles = titles
        

class CoachPlayer(Player, Coach):
    def __init__(self, name, team_name, years_of_experience, titles, hair_color, hair_length, skin_color, continent, goals, assists, position):
        # Inicializa a parte Player
        Player.__init__(self, name, team_name, hair_color, hair_length, skin_color, continent, goals, assists, position)
        # Inicializa a parte Coach
        Coach.__init__(self, name, years_of_experience, titles)

    def display_info(self):
        info = (f"Name: {self.name}\n"
                f"Club: {self.team_name}\n"
                f"Years of Experience: {self.years_of_experience}\n"
                f"Titles: {self.titles}")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("CoachPlayer Information", info)
        root.destroy()
        
import tkinter as tk
from tkinter import simpledialog, messagebox        
        
class ManagementSystem:
    
    def __init__(self, players_list):
        self.players = players_list  # Isso deve ser uma lista de jogadores
        self.coach_players = []

    def promote_to_coach_player(self, player, years_of_experience, titles):
        # A função agora espera um objeto 'player', além dos outros parâmetros
        # Adiciona os parâmetros faltantes para a criação de um CoachPlayer
        self.coach_players.append(CoachPlayer(player.name, player.team_name, years_of_experience, titles, player.hair_color, player.hair_length, player.skin_color, player.continent, player.goals, player.assists, player.position))
        #print(f"{player.name} has been promoted to CoachPlayer.")
        
    def print_coach_players(self):
        if not self.coach_players:
            print("No CoachPlayers found.")
            return
        for coach_player in self.coach_players:
            print(f"Name: {coach_player.name}, Club: {coach_player.team_name}, Years of Experience: {coach_player.years_of_experience}, Titles: {coach_player.titles}")

 
    def get_coach_players_info(self):
        info = "List of Coach/Players:\n"
        for player in self.coach_players:
        # Corrige o nome do atributo para 'years_of_experience'
            info += f"Name: {player.name},team:{player.team_name}  , Experience Years: {player.years_of_experience}, Titles: {player.titles}\n"
        return info
 
 
 
    def show_coach_players(management_system):
        
    # Agora, a função espera uma instância de ManagementSystem como argumento
        info = management_system.get_coach_players_info()  # Chama o método da instância
        root = tk.Tk()
        root.withdraw()
        new_window = tk.Toplevel(root)  # Cria uma nova janela com referência a 'root'.
        new_window.title("Coach/Players List")
        tk.Label(new_window, text=info, justify=tk.LEFT).pack(padx=10, pady=10)
        
        
        

# Supondo que 'management_system' seja uma instância de ManagementSystem que você criou em algum lugar.
# Certifique-se de que management_system esteja definido e acessível.
# Exemplo de inicialização de ManagementSystem (adicione seus jogadores conforme necessário).


 
        
def promote_player():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal do Tkinter.

    # Solicita o nome do jogador
    player_name = simpledialog.askstring("Promote Player", "Which player do you want to promote to coach?")
    
    if player_name:
        player_name_lower = player_name.lower()
        found = False

        # Solicita os anos de experiência e o número de títulos
        years_of_experience = simpledialog.askinteger("Years of Experience", "Enter the player's years of experience:", minvalue=0, maxvalue=100)
        titles = simpledialog.askinteger("Number of Titles", "Enter the player's number of titles won:", minvalue=0, maxvalue=100)

        if years_of_experience is not None and titles is not None:
            for player in players_list:
                if player.name.lower() == player_name_lower:
                    messagebox.showinfo("Success", f"{player_name} has been found and was promoted to coach/player with {years_of_experience} years of experience and {titles} titles.")
                    management_system.promote_to_coach_player(player, years_of_experience, titles)  # Passa o objeto 'player' diretamente
                    found = True
                    break
        
        if not found:
            messagebox.showerror("Error", "Player not found. Please insert a player that already exists.")
    else:
        messagebox.showinfo("Cancelled", "Operation cancelled by user.")
    
    root.destroy() 




management_system = ManagementSystem(players_list)









class PhotoPlayer(Player):
    def __init__(self, name, team_name, hair_color, hair_length, skin_color, continent, goals, assists, position, photo_extension='.png', photo_directory='faces'):
        super().__init__(name, team_name, hair_color, hair_length, skin_color, continent, goals, assists, position)
        
        # Construir o caminho do arquivo de foto
        photo_file = f"{name.replace(' ', '_')}{photo_extension}"  # Substituindo espaços por underscore para nomes compostos
        self.photo_path = os.path.join(photo_directory, photo_file)

        # Carregar a foto usando PIL
        try:
            self.photo_image = Image.open(self.photo_path)
            self.photo_image_tk = ImageTk.PhotoImage(self.photo_image)
        except FileNotFoundError:
        #    print(f"Arquivo não encontrado: {self.photo_path}")
            self.photo_image = None
            self.photo_image_tk = None
        except Exception as e:
         #   print(f"Erro ao carregar a foto: {e}")
            self.photo_image = None
            self.photo_image_tk = None
def resize_image(image, max_width, max_height):
    original_width, original_height = image.size

    # Calcula o ratio de redimensionamento mantendo a proporção, sem ampliar a imagem
    ratio = 0.7
    new_size = (int(original_width * ratio), int(original_height * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)


import tkinter as tk
from PIL import Image, ImageTk
import math

def resize_image(image, target_width, target_height):
    original_width, original_height = image.size
    ratio = min(target_width / original_width, target_height / original_height, 1)
    new_size = (int(original_width * ratio), int(original_height * ratio))
    return image.resize(new_size, Image.Resampling.LANCZOS)




import tkinter as tk
from tkinter import simpledialog, messagebox, Button

def update_player_stats(player):
    
    if tk._default_root:
        tk._default_root.destroy() 
        
        
    def add_goals():
        # Chamada modificada para incluir a janela pai
        amount_str = simpledialog.askstring("Input", "How many goals do you want to add? (Enter a positive integer)", parent=stats_window)
        try:
            amount = int(amount_str)
            if amount > 0:
                player.goals += amount
                # Janela pai especificada na chamada
                messagebox.showinfo("Success", f"Goals updated. {player.name} now has {player.goals} goals.", parent=stats_window)
                stats_window.destroy()
                display_menu(players_list)
            else:
                raise ValueError
        except ValueError:
            # Janela pai especificada na chamada
            messagebox.showerror("Error", "Invalid input. Please enter a positive integer.", parent=stats_window)

    def add_assists():
        # Chamada modificada para incluir a janela pai
        amount_str = simpledialog.askstring("Input", "How many assists do you want to add? (Enter a positive integer)", parent=stats_window)
        try:
            amount = int(amount_str)
            if amount > 0:
                player.assists += amount
                # Janela pai especificada na chamada
                messagebox.showinfo("Success", f"Assists updated. {player.name} now has {player.assists} assists.", parent=stats_window)
                stats_window.destroy()
                display_menu(players_list)
            else:
                raise ValueError
        except ValueError:
            # Janela pai especificada na chamada
            messagebox.showerror("Error", "Invalid input. Please enter a positive integer.", parent=stats_window)

    
       
    # Cria uma nova janela para atualizar as estatísticas do jogador
    stats_window = tk.Toplevel()
    stats_window.title("Update Player Stats")
     

    # Adiciona botões para adicionar gols e assistências
    ##Button(stats_window, text="Add Goals", command=add_goals).pack(pady=10)
    #Button(stats_window, text="Add Assists", command=add_assists).pack(pady=10)
    
    # Configura o layout da janela
    tk.Label(stats_window, text=f"Update stats for {player.name}:").pack(pady=10)
    tk.Button(stats_window, text="Add Goals", command=add_goals).pack(fill='x', expand=True, padx=20, pady=5)
    tk.Button(stats_window, text="Add Assists", command=add_assists).pack(fill='x', expand=True, padx=20, pady=5)



    stats_window.update_idletasks()  # Atualiza o layout da janela para obter dimensões corretas
    window_width = stats_window.winfo_width()
    window_height = stats_window.winfo_height()
    screen_width = stats_window.winfo_screenwidth()
    screen_height = stats_window.winfo_screenheight()
    x_coordinate = int((screen_width / 2) - (window_width / 2))
    y_coordinate = int((screen_height / 2) - (window_height / 2))
    stats_window.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")



def display_menu( players):
    global question
    
    if tk._default_root:
        tk._default_root.destroy()  # Destroy the existing root window if it exists
    root = tk.Tk()  # Create a new Tkinter window
    root.title("Menu")

    # Maximize the window
    root.state('zoomed')


    # Ajuste das dimensões
    frame_width = 300  # Largura dos frames laterais
    cols = 4  # Número de colunas para as imagens

    # Frame esquerdo
    left_frame = tk.Frame(root, width=frame_width)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Frame central para botões, ajustado para ser menor
    center_frame = tk.Frame(root, width=200)  # Background para visualizar o frame
    center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    # Frame direito
    right_frame = tk.Frame(root, width=frame_width)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Centralizando botões no frame central
    button_container = tk.Frame(center_frame)
    button_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    buttons = [
    ("1. New Game", lambda: select_team(root, players_list)),
    ("2. View Record List: Easy", lambda: Record.display_records(1)),
    ("3. View Record List: Medium", lambda: Record.display_records(2)),
    ("4. View Record List: Hard", lambda: Record.display_records(3)),
    ("5. Add goals or assists ", lambda: showplayers(players_list,3)),
    ("6. Total goals of 2 players ", lambda: showplayers(players_list,4)),
    ("7. Promote to coach player ", lambda: promote_player()),
    ("8. Show coaches/players ", lambda: ManagementSystem.show_coach_players(management_system)),
    ("9. Watch best goals video", play_video),
    ("10. Exit ", lambda: sys.exit()),
    # Adicione outras opções aqui conforme necessário
    ]
    
    for text, action in buttons:
        button = tk.Button(button_container, text=text, command=action)
        button.pack(pady=5)
    
    
    
    
    # Função para exibir imagens nos frames laterais
    def display_player_photos(frame, players_subset, cols):
        row = 0
        for i, player in enumerate(players_subset):
            if hasattr(player, 'photo_image') and player.photo_image:
                target_width = frame_width // cols
                target_height = 200  # Ajuste da altura das imagens
                resized_image = resize_image(player.photo_image, target_width, target_height)
                player_photo_tk = ImageTk.PhotoImage(resized_image)
                photo_label = tk.Label(frame, image=player_photo_tk)
                photo_label.image = player_photo_tk  # Mantenha referência
                photo_label.grid(row=i // cols, column=i % cols, padx=5, pady=5, sticky="nsew")
                frame.grid_columnconfigure(i % cols, weight=1)
                row = max(row, i // cols)
        frame.grid_rowconfigure(row, weight=1)

    # Divisão dos jogadores entre os frames laterais
    half_players = len(players) // 2
    players_left = players[:half_players]
    players_right = players[half_players:]

    # Exibindo imagens
    display_player_photos(left_frame, players_left, cols)
    display_player_photos(right_frame, players_right, cols)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
# Supondo que você tenha uma lista de objetos 'players' com um atributo 'photo_image' válido



def showplayers(players, menu):
    global user_selected_player 
    global players_list
    global guess_input
    

    if tk._default_root:
        tk._default_root.destroy()  # Destroy existing root window if exists
    root = tk.Tk()  # Create a new Tkinter window
    root.title("Player Profiles")

    # Maximize the window
    root.state('zoomed')

    # Create a Canvas and a Scrollbar
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the scrollable frame to be the canvas's window
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Layout Canvas and Scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Frame width and number of columns for images
    frame_width = root.winfo_screenwidth()  # Frame width based on screen width
    cols = 8  # Number of columns for images
    target_width = frame_width // cols
    target_height = 200   # Adjust image height

    def select_player(player):
        global user_selected_player
        global guess_input
        global question
        global player1 
        global player2 
        global player_selection_count
               
        confirmation = messagebox.askyesno("Confirm Selection", f"Are you sure that you want to select {player.name}?")
        if confirmation:
            if menu==1:
                user_selected_player = player
                messagebox.showinfo("Player Selected", f"You selected: {user_selected_player.name}")
               # print(f"Selected player: {user_selected_player.name}")
            if menu==2:
                guess_input=player
                messagebox.showinfo("Player Selected", f"You selected: {guess_input.name}")
                #print(f"Selected player: {guess_input.name}")
               # guess_input = user_selected_player
                question = 8
                #print("entra 503")
                #print(question)
                #print(guess_input.name)
               # Gameplay.check_right_player(guess_input )
            if menu==3:
                selected_player = player
                messagebox.showinfo("Player Selected", f"You selected: {selected_player.name}  to add goals or assists")
                update_player_stats(selected_player)        
            elif menu == 4:
            # Lógica para selecionar dois jogadores
                if player_selection_count == 0:
                    player1 = player
                    player_selection_count += 1
                    messagebox.showinfo("Player 1 Selected", f"You selected: {player1.name} as Player 1. Select another player.")
                    
                elif player_selection_count == 1:
                    player2 = player
                    player_selection_count += 1
                    messagebox.showinfo("Player 2 Selected", f"You selected: {player2.name} as Player 2.")
                # Após selecionar ambos os jogadores, você pode resetar player_selection_count se necessário
                # ou proceder com a lógica que envolve os dois jogadores selecionados
                    print(f"Selected players: {player1.name} and {player2.name}")
                # Resetar a contagem se você espera mais seleções ou prosseguir com a lógica envolvendo ambos os jogadores
                    player_selection_count = 0
                    combined_player_goals = player1.goals + player2.goals

# Exibe a mensagem com a soma dos gols
                    messagebox.showinfo("Combined Goals", f"The combined goals of {player1.name} and {player2.name} are: {combined_player_goals}")
                    player1=None
                    player2=None
                    
                    display_menu(players_list)
                    root.destroy()
            if menu!=4:
                root.destroy()    
                
                
                
    def display_players():
        for i, player in enumerate(players):
            
            col = i % cols
            row = (i // cols) * 7  # Each player's information takes up 7 rows including the select button

            if hasattr(player, 'photo_image') and player.photo_image:
                resized_image = resize_image(player.photo_image, target_width, target_height)
                player_photo_tk = ImageTk.PhotoImage(resized_image)

                photo_label = tk.Label(scrollable_frame, image=player_photo_tk)
                photo_label.image = player_photo_tk  # Keep reference
                photo_label.grid(row=row, column=col, padx=5, pady=5)

                select_button = tk.Button(scrollable_frame, text="Select Player", command=lambda p=player: select_player(p))
                select_button.grid(row=row+1, column=col, padx=5, pady=5)

                tk.Label(scrollable_frame, text=f"Name: {player.name}").grid(row=row+2, column=col, padx=5, sticky="w")
                tk.Label(scrollable_frame, text=f"Continent: {player.continent}").grid(row=row+3, column=col, padx=5, sticky="w")
                tk.Label(scrollable_frame, text=f"Goals: {player.goals}").grid(row=row+4, column=col, padx=5, sticky="w")
                tk.Label(scrollable_frame, text=f"Assists: {player.assists}").grid(row=row+5, column=col, padx=5, sticky="w")
                tk.Label(scrollable_frame, text=f"Position: {player.position}").grid(row=row+6, column=col, padx=5, sticky="w")

    def display_questions():
        question_options = [
            "1. Does the player have light hair?",
            "2. Does the player have short hair?",
            "3. Is the player tanned?",
            "4. Original continent:",
            "5. Goals last season:",
            "6. Assists last season:",
            "7. Position:",
           
        ]

        def question_selected(option):
            global question
          #  print(f"You selected: {question_options[option]}")
            
            if option == 7:
                guess = simpledialog.askstring("Guess the Player", "Enter your guess:")
                print(f"Your guess: {guess}")
                # Here would add the logic to check the guess
            question=option +1   
            root.destroy()
           
        
        for index, option in enumerate(question_options):
            tk.Button(scrollable_frame, text=option, command=lambda idx=index: question_selected(idx)).grid(row=index, column=cols+2, sticky="ew")
       
    
    # Add "Main Menu" and "Exit" buttons for both menus
    if menu == 1 or menu==3 or menu==4:
        display_players()
    elif menu == 2:

        display_players()
        display_questions()
    global players_list    
    
    main_menu_button = tk.Button(scrollable_frame, text="Main Menu", command=lambda: display_menu(players_list))  # Substitua pelo comando real

    main_menu_button.grid(row=8, column=10, padx=20, pady=20, sticky="nsew")  # Adjusted to the second last column

    exit_button = tk.Button(scrollable_frame, text="Exit", command=lambda: root.destroy())
    exit_button.grid(row=15, column=10 , padx=20, pady=20, sticky="nsew")  # Adjusted to the last column

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
  
            
# Class to manage the type of game and its mechanics
class TypeOfGame:
    
    user_selected_player = None
    right_questions_player = 0
    right_questions_opponent = 0
    level = 0
    user_questions = 0
    level3Questions = 0
    opponent_questions = []
    opponent_guesses = []

    def __init__(self, all_players):
        self._all_players = all_players
        self._user_available_players = []
        self._bot_available_players = []
        self._bot_flag = False 
        self._end_game_flag = False

    # Property decorators and setters for game attributes
    @property
    def all_players(self):
        return self._all_players

    @all_players.setter
    def all_players(self, value):
        self._all_players = value

    @property
    def user_available_players(self):
        return self._user_available_players

    @user_available_players.setter
    def user_available_players(self, value):
        self._user_available_players = value

    @property
    def bot_available_players(self):
        return self._bot_available_players

    @bot_available_players.setter
    def bot_available_players(self, value):
        self._bot_available_players = value

    @property
    def bot_flag(self):
        return self._bot_flag

    @bot_flag.setter
    def bot_flag(self, value):
        self._bot_flag = value

    @property
    def end_game_flag(self):
        return self._end_game_flag

    @end_game_flag.setter
    def end_game_flag(self, value):
        self._end_game_flag = value


    def start_game(self,root, chosen_team_player, chosen_team_computer):
        global user_selected_player
        global mix
        # Begin the start_game method. It takes chosen teams for player and computer as arguments.
        if not mix:
            # If mix is not True, segregate players based on the team.
            team_players_player = [player for player in self.all_players if player.team_name.lower() == chosen_team_player.lower()]
            team_players_computer = [player for player in self.all_players if player.team_name.lower() == chosen_team_computer.lower()]
            # Assign segregated players to user and bot.
            self.user_available_players = team_players_player
            self.bot_available_players = team_players_computer
        else:
            # If mix is True, select 24 random players from all players.
            team_players_player = random.sample(self.all_players, 24)
            team_players_computer = team_players_player
            # Assign the same players to both user and bot.
            self.user_available_players = team_players_player
            self.bot_available_players = team_players_computer
            mix=False
            
        def set_difficulty(level):
            TypeOfGame.level = level
            level_names = {1: "Easy", 2: "Normal", 3: "Hard"}
            messagebox.showinfo("Difficulty Selected", f"Difficulty level set to: {level_names[level]}")
            # Aqui você pode fechar a janela de seleção de dificuldade ou fazer outras ações necessárias
            difficulty_window.destroy()
            root.destroy()
            # Supondo que você queira fechar a janela após a seleção
    
        difficulty_window = tk.Tk()
        difficulty_window.title("Select Difficulty Level")


        # Define as dimensões da janela
        window_width = 300
        window_height = 150

        # Obtém as dimensões da tela
        screen_width = difficulty_window.winfo_screenwidth()
        screen_height = difficulty_window.winfo_screenheight()
        # Calcula a posição x e y para centralizar a janela
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)

        # Configura a janela para abrir no centro da tela
        difficulty_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        label = tk.Label(difficulty_window, text="Choose the difficulty level:")
        label.pack(pady=10)

        # Adiciona botões para cada nível de dificuldade
        btn_easy = tk.Button(difficulty_window, text="1: Easy", command=lambda: set_difficulty(1))
        btn_easy.pack(fill='x')

        btn_normal = tk.Button(difficulty_window, text="2: Normal", command=lambda: set_difficulty(2))
        btn_normal.pack(fill='x')

        btn_hard = tk.Button(difficulty_window, text="3: Hard", command=lambda: set_difficulty(3))
        btn_hard.pack(fill='x')
        root.protocol("WM_DELETE_WINDOW", on_close)    
        difficulty_window.mainloop()
        
        
        

        
        
        #print(f"Available players for {chosen_team_player}:")
        #for player in team_players_player:
         #   player.display_info()
        #print("entra aqui 555")
        #user_selected_player = None
        if tk._default_root:
         #   print("entra aqui 558")
            tk._default_root.destroy()  # Destroy the existing root window if it exists
        #print("entra aqui 560")
       
        showplayers(self.user_available_players,1)
        

        window = tk.Tk()
        window.title("Game Selection")
        window.state('zoomed')
        

    # Define o tamanho da janela
        window.geometry("400x200")
        if user_selected_player:
        # Se um jogador válido é selecionado, seleciona aleatoriamente um jogador para o bot.
            user_player_text = f"Your player is: {user_selected_player.name}"
            user_player_label = tk.Label(window, text=user_player_text)
            user_player_label.pack()

            bot_player = random.choice(team_players_computer)
            bot_player_text = f"Opponent player selected!"
            print(bot_player.name)
            bot_player_label = tk.Label(window, text=bot_player_text)
            bot_player_label.pack()

            img_path = "logos/int.png"  # Caminho relativo à imagem
            img = ImageTk.PhotoImage(file=img_path)
            img_label = tk.Label(window, image=img)
            img_label.image = img  # Mantenha uma referência
            img_label.pack()

    # Botão para fechar a janela
        close_button = tk.Button(window, text="Let's go!", command=window.destroy)
        close_button.pack()
        
        #root.protocol("WM_DELETE_WINDOW", on_close)
        window.mainloop()


        while user_selected_player:
                # Game loop continues until the end_game_flag is set to True.
                Gameplay.bot_flag = False
                self.bot_available_players = Gameplay.ask_bot_question(self, bot_player, self.bot_available_players)
                if TypeOfGame.right_questions_player >= 3:
                    user_selected_player = random.choice(self.user_available_players)
                    messagebox.showinfo("Opponent guessed 3 questions.", f"Your new player is: {user_selected_player.name}")
                    self.user_available_players = team_players_player

                

                    TypeOfGame.right_questions_player = 0
                    Gameplay.opponent_questions.clear()
                    Gameplay.opponent_guesses.clear()
                    Gameplay.level3Questions = 0
                Gameplay.user_questions += 1
                Gameplay.bot_flag = True
                #print("true.751")
                self.user_available_players = Gameplay.ask_bot_question(self, user_selected_player, self.user_available_players)
                if TypeOfGame.right_questions_opponent >= 3:
                    # If the opponent (bot) gets 3 right questions, automatically select a new player for it.
                    
                    messagebox.showinfo(f"Opponent guessed 3 questions. Automatic selection of a new player for him")
                    self.bot_available_players = team_players_computer
                    bot_player = random.choice(team_players_computer)
                    print(f"bot new  player : {bot_player.name} selected!")
                    TypeOfGame.right_questions_opponent = 0
                Gameplay.bot_flag = False
                    
        else:
            print("Player not found. Please enter a valid player name.")

# Class to handle records of user's game
class Record( TypeOfGame):
    def __init__(self, username, level, num_questions, date):
        self.username=username
        TypeOfGame.__init__(self, level)  # Altere conforme necessário
        self.num_questions = int(num_questions)
        self.date = date
       
      
    
    @staticmethod
    def display_records(file_number):
        if file_number not in [1, 2, 3]:
            messagebox.showerror("Invalid Input", "Please enter 1, 2 or 3.")
            return

        record_filename = f'records{file_number}.csv'

        try:
            records = []

            if os.path.exists(record_filename):
                with open(record_filename, 'r') as csv_file:
                    csv_reader = csv.reader(csv_file)
                    for row in csv_reader:
                        if row and len(row) >= 3:
                             
                            #print(row[0])
                            #print(row[1])
                            #print(row[2])
                            records.append(Record((row[0]),(row[0]), int(row[1]), row[2]))
            #print("entra aqui 840")            
            # Ordenar registros com base no número de perguntas em ordem ascendente
            sorted_records = sorted(records, key=lambda x: x.num_questions)

            # Cria uma nova janela para exibir os registros
            records_window = tk.Toplevel()
            records_window.title(f"Record List - Difficulty {file_number}")

            # Cria uma Treeview para exibir os registros
            columns = ('position', 'username', 'num_questions', 'date')
            tree = ttk.Treeview(records_window, columns=columns, show='headings')
            
            # Define as colunas
            tree.heading('position', text='Position')
            tree.heading('username', text='Username')
            tree.heading('num_questions', text='Num Questions')
            tree.heading('date', text='Date')

            # Adiciona os registros na Treeview
            for position, record in enumerate(sorted_records, start=1):
                tree.insert('', 'end', values=(position, record.username, record.num_questions, record.date))

            # Configura o tamanho das colunas
            for col in columns:
                tree.column(col, width=100)
                tree.heading(col, text=col.capitalize())

            tree.pack(expand=True, fill='both')

        except Exception as e:
            messagebox.showerror("Error", f"Error displaying records from CSV: {e}")




        
class Gameplay(TypeOfGame):
  
    #method to save the recors
    @staticmethod
    def save_records(username, num_questions, date, file_number):
        record_filename = f'records{file_number}.csv'

        try:
            with open(record_filename, 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([username, num_questions, date])

        except Exception as e:
            print(f"Error saving records to CSV: {e}")
     #method to display the records       
    
    #method with the questions. for the opponent and the player
    @staticmethod
    def ask_bot_question(game_instance, selected_player, user_available_players):
        global question
        global guess_input
        

            
        
    #    question_options = [
     #       "1. Does the player have light hair?",
      #      "2. Does the player have short hair?",
       #     "3. Is the player tanned?",
        #    "4. Original continent:",
         #   "5. Goals last season:",
          #  "6. Assists last season:",
           # "7. Position:",
            #"8. Guess player:"
        #]
                #flag that exists to control the flow of the game and automatize questions when is bot asking
        if not Gameplay.bot_flag:

            showplayers(user_available_players,2)
            #print(question)
            #print("837")
            while (not Gameplay.bot_flag ):
                #question_input = question

                if question  <=  7:
                    
                    #print("Your question:", question_options[int(question_input) - 1])
                    #print("human", TypeOfGame.right_questions_player)
                    #print("bot", TypeOfGame.right_questions_opponent)
                    #print("faz a pergunta851")
                    return Gameplay.process_question(question, selected_player, user_available_players)
                elif question == 8:
                    #print("What's your guess?")
                    guess_input = guess_input.name.lower()
                    if guess_input == selected_player.name.lower():
                        
                        Gameplay.opponent_questions.clear()
                        TypeOfGame.right_questions_player=0
                        TypeOfGame.right_questions_opponent=0
                        Gameplay.level=0
                        Gameplay.level3Questions=0
                        Gameplay.opponent_guesses.clear()
                        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        TypeOfGame.end_game_flag=True
                        show_gifs(1)
                        
                        if TypeOfGame.level == 1:
                            Gameplay.save_records(username, Gameplay.user_questions, current_date, 1)

                            Gameplay.user_questions=0
                        elif TypeOfGame.level == 2:
                            Gameplay.save_records(username, Gameplay.user_questions, current_date, 2)
                            Gameplay.user_questions=0
                        
                        else:
                            Gameplay.save_records(username, Gameplay.user_questions, current_date, 3)
                            Gameplay.user_questions=0
                        display_menu(players_list)    
                        return user_available_players                       
                        
                        
                    else:
                        messagebox.showinfo("You are Wrong. Best of luck next time!")
                        #print("You are Wrong. Best of luck next time!")
                    return user_available_players
                else:
                    print("Invalid option. Please choose a number between 1 and 8.")

        elif TypeOfGame.level == 1 and len(user_available_players) <= 10:
            Gameplay.bot_flag = False

           # print("I'm going to guess!. Is it this one?")
            choice = random.choice(user_available_players)
            messagebox.showinfo("I'm going to guess!", f"Is it this one? {choice.name}")

            print(choice.name)

            if choice == selected_player:
                
                #print("The opponent guessed your player. You lost.")
                Gameplay.opponent_questions.clear()
                TypeOfGame.right_questions_player=0
                TypeOfGame.right_questions_opponent=0
                Gameplay.level=0
                Gameplay.user_questions=0
                Gameplay.level3Questions=0
                Gameplay.opponent_guesses.clear()
                TypeOfGame.end_game_flag=True
                show_gifs(2)
                display_menu(players_list)
            return user_available_players
        elif TypeOfGame.level == 2 and len(user_available_players) <= 5:
            Gameplay.bot_flag = False
            
            choice = random.choice(user_available_players)
            while choice in Gameplay.opponent_guesses:
                choice = random.choice(user_available_players)
            messagebox.showinfo("I'm going to guess!", f"Is it this one? {choice.name}")
            Gameplay.opponent_guesses.append(choice)
            #print(choice.name)

            if choice == selected_player:
                
                Gameplay.opponent_questions.clear()
                TypeOfGame.right_questions_player=0
                TypeOfGame.right_questions_opponent=0
                Gameplay.level=0
                Gameplay.user_questions=0
                Gameplay.level3Questions=0
                Gameplay.opponent_guesses.clear()
                TypeOfGame.end_game_flag=True
                show_gifs(2)
                display_menu(players_list)
            return user_available_players
        elif TypeOfGame.level == 3 and len(user_available_players) <= 3:
            Gameplay.bot_flag = False
           
            choice = random.choice(user_available_players)
            

            while choice in Gameplay.opponent_guesses:
                choice = random.choice(user_available_players)
            Gameplay.opponent_guesses.append(choice)
            messagebox.showinfo("I'm going to guess!", f"Is it this one? {choice.name}")
            

            if choice == selected_player:
                
                Gameplay.opponent_questions.clear()
                TypeOfGame.right_questions_player=0
                TypeOfGame.right_questions_opponent=0
                Gameplay.level=0
                Gameplay.user_questions=0
                Gameplay.level3Questions=0
                Gameplay.opponent_guesses.clear()
                TypeOfGame.end_game_flag=True
                show_gifs(2)
                display_menu(players_list)
            return user_available_players
        elif TypeOfGame.level == 3 and len(user_available_players) >= 3:
            
            goals_median, assists_median = user_available_players[0].calculate_goals_and_assists_median(user_available_players)    
            if Gameplay.level3Questions==0:
                question=5
                #print("1pergunta nivel 3")
                
                
            elif Gameplay.level3Questions==1 and assists_median>=1:
                question=6
               # print("2pergunta nivel3")     
            
            elif len(Gameplay.opponent_questions) <= 4:
                # print(len(Gameplay.opponent_questions))
                available_questions = [1, 2, 3, 4, 7]
                available_questions = [q for q in available_questions if q not in Gameplay.opponent_questions]
                question_number = random.choice(available_questions)
                question = str(question_number)
                Gameplay.opponent_questions.append(question_number)
                #print("3,4,5,6,7 pergunta nivel 3")
                #return user_available_players
                #print("Selected question:", question)
                question = int(question_number)
                print("975")
                print(question)
                
            else:
                # print("Selected question:", question)
                question = random(5, 6)
                print("entra 978")
            
            #print(" ultima pergunta nivel 3")  
            #print(Gameplay.bot_flag)  
            #print("Other player question-Entrou 2 pergunta")
            #print(question)
            #question = str(random.randint(5, 5))
            return Gameplay.process_question(question, selected_player, user_available_players)
            
            
        else:
            question = random.randint(1, 7)
            if TypeOfGame.level == 2:
                question_number = question
                while question_number in Gameplay.opponent_questions:
                    question = random.randint(1, 7)
                    question_number = question
                # print("Opponent guesses:", Gameplay.opponent_questions)    
                if question_number in [1, 2, 3, 4, 7]:
                    Gameplay.opponent_questions.append(question_number)
                #print("perguntas random com sem repetir nivel 2")
               # print("primeira pergunta medio bot")            
            elif TypeOfGame.level == 1:
                #print("pergunta random nivel 1 ")
                question = random.randint(1, 7)
           #print("Other player question", question_options[int(question) - 1])
            #print("human", TypeOfGame.right_questions_player)
            #print("bot", TypeOfGame.right_questions_opponent)
                #print("primeira pergunta facil bot")
                #print(question)
            return Gameplay.process_question(question, selected_player, user_available_players)
    

    #method that processes the question. that means that this method receive a question and automatically returns
    #the answer and the list of players available after that
    @staticmethod
    def process_question(question, selected_player, user_available_players):
        global selected_option 
        question_options = [
            "1. Does the player have light hair?",
            "2. Does the player have short hair?",
            "3. Is the player tanned?",
            "4. Original continent:",
            "5. Goals last season:",
            "6. Assists last season:",
            "7. Position:",
            "8. Guess player:"
        ]
        
        
        
        if Gameplay.bot_flag==False:
            root = tk.Tk()
            root.withdraw()
            
        if question == 1:
            correct_answer = "yes" if selected_player.hair_color.lower() == "light" else "no"
            #print(f"Bot's answer: {correct_answer}")
            if Gameplay.bot_flag==False:
                messagebox.showinfo("Bot's Answer", f"The bot's answer is: {correct_answer}")
                root.deiconify()  
            
            if correct_answer == "yes":
                if Gameplay.bot_flag == False:
                    TypeOfGame.right_questions_player += 1
                else:
                    TypeOfGame.right_questions_opponent += 1
                
                user_available_players = [player for player in user_available_players if player.hair_color.lower() == "light"]
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Bot's question is:", question_options[question - 1])
                    messagebox.showinfo("Answer", f"The correct answer is: {correct_answer}")
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")

                   # print("Players with light hair:")
                    #for player in user_available_players:
                     #   player.display_info()
            else:
                user_available_players = [player for player in user_available_players if player.hair_color.lower() == "dark"]
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Bot's question is:", question_options[question - 1])
                    messagebox.showinfo("Answer", f"The correct answer is: {correct_answer}")
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
                    #print("Players with dark hair:")
                #    for player in user_available_players:
                 #       player.display_info()
                #print("Players with dark hair:")
                #root.destroy()
                #showplayers(user_available_players, 2)

            
            
            
        elif question ==2:
            correct_answer = "yes" if selected_player.hair_length.lower() == "short" else "no"
            if Gameplay.bot_flag==False:
                messagebox.showinfo("Bot's Answer", f"The bot's answer is: {correct_answer}")
                root.deiconify()  
             
           # print(f"Bot's answer: {correct_answer}")

            if correct_answer == "yes":
                
                if Gameplay.bot_flag == False:
                    TypeOfGame.right_questions_player += 1
                else:
                    TypeOfGame.right_questions_opponent += 1
                
                
                
                user_available_players = [player for player in user_available_players if player.hair_length.lower() == "short"]
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Bot's question is:", question_options[question - 1])
                    messagebox.showinfo("Answer", f"The correct answer is: {correct_answer}")
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
                    #print("Players with short hair:")
                   # for player in user_available_players:
                    #    player.display_info()
            else:
                user_available_players = [player for player in user_available_players if player.hair_length.lower() == "long"]
                
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Bot's question is:", question_options[question - 1])
                    messagebox.showinfo("Answer", f"The correct answer is: {correct_answer}")
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
                    #print("Players with long hair:")
                   # for player in user_available_players:
                    #    player.display_info()
        elif question == 3:
            correct_answer = "yes" if selected_player.skin_color.lower() == "tanned" else "no"
            if Gameplay.bot_flag==False:
                
                messagebox.showinfo("Bot's Answer", f"The bot's answer is: {correct_answer}")
                root.deiconify()  

          #  print(f"Bot's answer: {correct_answer}")

            if correct_answer == "yes":
                if Gameplay.bot_flag == False:
                    TypeOfGame.right_questions_player += 1
                else:
                    TypeOfGame.right_questions_opponent += 1
                
                user_available_players = [player for player in user_available_players if player.skin_color.lower() == "tanned"]
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Bot's question is:", question_options[question - 1])
                    messagebox.showinfo("Answer", f"The correct answer is: {correct_answer}")
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
                    print("tanned player")
                   # for player in user_available_players:
                    #    player.display_info()
                

                    
            else:
                user_available_players = [player for player in user_available_players if player.skin_color.lower() == "not tanned"]
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Bot's question is:", question_options[question - 1])
                    messagebox.showinfo("Answer", f"The correct answer is: {correct_answer}")
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
                    print("not tanned player")
                 #   for player in user_available_players:
                   #      player.display_info()

        elif question == 4:
            continent_mapping = {
                "1": "South America",
                "2": "America",
                "3": "Africa",
                "4": "Europe",
                "5": "Asia",
                "6": "Australia",
            }


            def select_continent(option):
                global selected_option
                selected_option = option
                print(f"Selected Option: {selected_option}")  # Apenas para demonstração
                # Aqui você pode adicionar qualquer lógica que deseje executar após a seleção
                # Por exemplo, fechar a janela ou processar a seleção
                root.destroy()
            
            if not Gameplay.bot_flag:
                if tk._default_root:
                    tk._default_root.destroy()
                    
                root = tk.Tk()
                root.title("Continent Selector")
                 
                root.state('zoomed')

                # Criação de um frame para os botões
                button_frame = tk.Frame(root)
                button_frame.pack(fill="both", expand=True)

                # Distribuição dos botões de continentes
                for number, continent in continent_mapping.items():
                    ttk.Button(button_frame, text=continent, command=lambda option=number: select_continent(option)).pack(side="top", fill="x", padx=20, pady=10)

                root.protocol("WM_DELETE_WINDOW", on_close)
                root.mainloop() 
                 
                 
            else:  # bot_flag=True
                selected_option = str(random.randint(1, 6))
                messagebox.showinfo("Bot question", f"Is this continent: {continent_mapping[selected_option]}?")
               
                
            # Verificar se a escolha é válida
            if selected_option in continent_mapping:
                selected_continent = continent_mapping[selected_option]

                # Comparar a resposta com a característica do jogador
                correct_answer = "yes" if selected_player.continent.lower() == selected_continent.lower() else "no"
                messagebox.showinfo("Correct answer", f" {correct_answer}!")

                # Filtrar jogadores com base na escolha do continente
                if correct_answer == "yes":
                  
                    user_available_players = [player for player in user_available_players if player.continent.lower() == selected_continent.lower()]
                    if correct_answer == "yes":
                     if Gameplay.bot_flag == False:
                        TypeOfGame.right_questions_player += 1
                     else:
                        TypeOfGame.right_questions_opponent += 1
                else:
                    
                    user_available_players = [player for player in user_available_players if player.continent.lower() != selected_continent.lower()]

                # Exibir jogadores disponíveis no continente selecionado
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
                   # print("Available players for the opponent")
                   # for player in user_available_players:
                    #    player.display_info()


            else:
                print("Invalid option. Please select a valid number.")
                
        
                  
        
        elif question == 5:
            global number_input
            
            if not Gameplay.bot_flag:
                if tk._default_root:
                    tk._default_root.destroy()
                   
                def set_option(option):
                    global selected_option
                    selected_option = option
    # Resetar a cor dos botões para o padrão
                    btn_greater_equal.config(bg="SystemButtonFace")
                    btn_less_than.config(bg="SystemButtonFace")
    # Muda a cor do botão selecionado para azul claro
                    if option == '1':
                        btn_greater_equal.config(bg="light blue")
                    elif option == '2':
                        btn_less_than.config(bg="light blue")

                def on_ok():
                    global number_input
                    global selected_option
                    try:
        # Tentativa de converter a entrada para float
                        number_input = float(goals_entry.get())
                        if number_input < 0:
                            raise ValueError("The number of goals cannot be negative.")
                        
                        print(f"Option Selected: {selected_option}, Number Input: {number_input}")
                        root.destroy()  # Fecha a janela após a coleta dos dados
                    except ValueError as e:
                        messagebox.showerror("Invalid Input", str(e))
                        goals_entry.delete(0, tk.END)
                
                def validate_digit_only(char):
                    return char.isdigit()


# Initialize the main window
                root = tk.Tk()
                root.title("Option Selection")
                root.state('zoomed')

            # Define the global variable to store the selected option
                selected_option = None

            # Create buttons
                btn_greater_equal = tk.Button(root, text="Greater than or equal to this value",
                              command=lambda: set_option('1'))
                btn_less_than = tk.Button(root, text="Less than this value",
                          command=lambda: set_option('2'))

# Position the buttons in the window
                btn_greater_equal.pack(pady=10)
                btn_less_than.pack(pady=10)

# Start the main loop of the graphical interface
                goals_entry_label = tk.Label(root, text="Please enter the number of goals:")
                goals_entry_label.pack(pady=(10, 0))
                vcmd = (root.register(validate_digit_only), '%S')  # %S representa o caractere inserido
                goals_entry = tk.Entry(root, validate='key', validatecommand=vcmd)
                goals_entry.pack(pady=5)
                
                
                
                ok_button = tk.Button(root, text="OK", command=on_ok)
                ok_button.pack(pady=20)

# Inicia o loop principal da interface gráfica
                root.protocol("WM_DELETE_WINDOW", on_close)
                root.mainloop() 
                #selected_option = input("More or less than?: Type 1 for greater than or equal to this value, and 2 for less than this value. ")
                #number_input = int(input("How many goals? "))
            else:
                #print("entra 1165")
                selected_option = str(random.randint(1, 2))
                number_input = random.randint(0, 15)
                #print(f"selected_option: {selected_option}, number_input: {number_input} goals last season")
                if TypeOfGame.level==3:
                    selected_option='1'
                    goals_median, assists_median = user_available_players[0].calculate_goals_and_assists_median(user_available_players)
                    
                    number_input=int(goals_median)    
                    Gameplay.level3Questions+=1
                    
            if selected_option == '1':
                
                #print(f"{number_input} or more goals?")
                condition = selected_player.goals >= number_input
                if condition == True:
                    if Gameplay.bot_flag == False:
                        TypeOfGame.right_questions_player += 1
                        
                    else:
                        TypeOfGame.right_questions_opponent += 1
                    user_available_players = [player for player in user_available_players if player.goals >= number_input]
                else:
                    user_available_players = [player for player in user_available_players if player.goals < number_input]
                if condition==True:
                    message = f"{number_input} or more goals "
                    
                else:
                    message = f"fewer than {number_input} goals"   
                    
                
            elif selected_option == '2':
                #print(f"less than {number_input} goals? ")
                condition = selected_player.goals < number_input
                if condition == True:
                    if Gameplay.bot_flag == False:
                        TypeOfGame.right_questions_player += 1
                    else:
                        TypeOfGame.right_questions_opponent += 1
                    
                    user_available_players = [player for player in user_available_players if player.goals < number_input]
                else:
                    user_available_players = [player for player in user_available_players if player.goals >= number_input]
                if condition==True:
                    message = f"fewer than {number_input} goals"
                else:
                    message = f"{number_input} or more goals "    
            else:
                #print("Invalid option. Please select '1' for more or '2' for less.")
                return user_available_players

            correct_answer = "yes" if condition else "no"
            #print(f"Bot's answer: {correct_answer}")
            #print(f"{message} - Available players:")
            if Gameplay.bot_flag==True:
                messagebox.showinfo("Bot question:", f"Bot's question: {message}\nThe correct answer is: {correct_answer}")
                messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
               # for player in user_available_players:
                #    player.display_info()
            else:
                messagebox.showinfo("Bot answer", f"The correct answer is: {correct_answer}")
                
        elif question == 6:
            if not Gameplay.bot_flag:
                if tk._default_root:
                    tk._default_root.destroy()
                    
                    
                def set_option(option):
                    global selected_option
                    selected_option = option
    # Resetar a cor dos botões para o padrão
                    btn_greater_equal.config(bg="SystemButtonFace")
                    btn_less_than.config(bg="SystemButtonFace")
    # Muda a cor do botão selecionado para azul claro
                    if option == '1':
                        btn_greater_equal.config(bg="light blue")
                    elif option == '2':
                        btn_less_than.config(bg="light blue")

                def on_ok():
                    global number_input
                    global selected_option
                    try:
        # Tentativa de converter a entrada para float
                        number_input = float(goals_entry.get())
                        if number_input < 0:
                            raise ValueError("The number of assists cannot be negative.")
                        
                        print(f"Option Selected: {selected_option}, Number Input: {number_input}")
                        root.destroy()  # Fecha a janela após a coleta dos dados
                    except ValueError as e:
                        messagebox.showerror("Invalid Input", str(e))
                        goals_entry.delete(0, tk.END)
                
                def validate_digit_only(char):
                    return char.isdigit()    
                    
                    
                root = tk.Tk()
                root.title("Option Selection")
                root.state('zoomed')

            # Define the global variable to store the selected option
                selected_option = None

            # Create buttons
                btn_greater_equal = tk.Button(root, text="Greater than or equal to this value",
                              command=lambda: set_option('1'))
                btn_less_than = tk.Button(root, text="Less than this value",
                          command=lambda: set_option('2'))

# Position the buttons in the window
                btn_greater_equal.pack(pady=10)
                btn_less_than.pack(pady=10)

# Start the main loop of the graphical interface
                goals_entry_label = tk.Label(root, text="Please enter the number of assists:")
                goals_entry_label.pack(pady=(10, 0))
                vcmd = (root.register(validate_digit_only), '%S')  # %S representa o caractere inserido
                goals_entry = tk.Entry(root, validate='key', validatecommand=vcmd)
                goals_entry.pack(pady=5)
                
                
                
                ok_button = tk.Button(root, text="OK", command=on_ok)
                ok_button.pack(pady=20)    
                    
                root.protocol("WM_DELETE_WINDOW", on_close)
                root.mainloop() 
                #selected_option = input("More or less than?: Type 1 for greater than or equal to this value, and 2 for less than this value. ")
                #number_input = int(input("How many goals? "))    
                    
            else:
                #print("entra 1227")
                selected_option = str(random.randint(1, 2))
                number_input = random.randint(0, 15)
                #print(f"selected_option: {selected_option}, number_input: {number_input} goals last season")
                if TypeOfGame.level==3:
                    selected_option='1'
                    goals_median, assists_median = user_available_players[0].calculate_goals_and_assists_median(user_available_players)
                    
                    number_input=int(assists_median)    
                    Gameplay.level3Questions+=1

            if selected_option == '1':
                condition = selected_player.assists >= number_input
                if condition == True:
                    if Gameplay.bot_flag == False:
                        TypeOfGame.right_questions_player += 1
                    else:
                        print(f"{number_input} or more assists")
                        TypeOfGame.right_questions_opponent += 1
                    user_available_players = [player for player in user_available_players if player.assists >= number_input]
                
                else:
                    user_available_players = [player for player in user_available_players if player.assists < number_input]

                if condition==True:
                    message = f"{number_input} or more assists "
                else:
                    message = f"fewer than {number_input} assists"   
                    
            elif selected_option == '2':
                print(f"less than {number_input} assists")
                condition = selected_player.assists < number_input
                if condition == True:
                    user_available_players = [player for player in user_available_players if player.assists < number_input]
                    if Gameplay.bot_flag == False:
                        TypeOfGame.right_questions_player += 1
                    else:
                        TypeOfGame.right_questions_opponent += 1
                else:
                    user_available_players = [player for player in user_available_players if player.assists >= number_input]
                if condition==True:
                    message = f"fewer than {number_input} assists"
                else:
                    message = f"{number_input} or more assists "    
            else:
                print("Invalid option. Please select '1' for more or '2' for less.")
                return user_available_players

            correct_answer = "yes" if condition else "no"
          #  print(f"Bot's answer: {correct_answer}")
           # print(f"{message} - Available players:")

            if Gameplay.bot_flag==True:
                messagebox.showinfo("Bot question:", f"Bot's question: {message}\nThe correct answer is: {correct_answer}")
              #  for player in user_available_players:
               #     player.display_info()
            else:
                messagebox.showinfo("Bot answer", f"The correct answer is: {correct_answer}")
                messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")

        elif question == 7:
            position_mapping = {
                "1": "Goalkeeper",
                "2": "Defender",
                "3": "Midfielder",
                "4": "Forward",
            }
            def select_position(option):
                global selected_option
                selected_option = option
                print(f"Selected Option: {selected_option}")  # Apenas para demonstração
                # Aqui você pode adicionar qualquer lógica que deseje executar após a seleção
                # Por exemplo, fechar a janela ou processar a seleção
                root.destroy()
                    
            if not Gameplay.bot_flag:
                if tk._default_root:
                    tk._default_root.destroy()
                    
                root = tk.Tk()
                root.title("Continent Selector")
                 
                root.state('zoomed')

                # Criação de um frame para os botões
                button_frame = tk.Frame(root)
                button_frame.pack(fill="both", expand=True)

                # Distribuição dos botões de continentes
                for number, position in position_mapping.items():
                    ttk.Button(button_frame, text=position, command=lambda option=number: select_position(option)).pack(side="top", fill="x", padx=20, pady=10)
                
                root.protocol("WM_DELETE_WINDOW", on_close)
                root.mainloop()     
                    

            else:  # bot_flag=True 
                selected_option = str(random.randint(1, 4))
                messagebox.showinfo("Bot question", f"Is this position: {position_mapping[selected_option]}?")

            # Verificar se a escolha é válida
            if selected_option in position_mapping:
                selected_position = position_mapping[selected_option]

                # Comparar a resposta com a característica do jogador
                correct_answer = "yes" if selected_player.position.lower() == selected_position.lower() else "no"
                messagebox.showinfo("Correct answer", f" {correct_answer}!")

                # Filtrar jogadores com base na escolha da posicao
                if correct_answer == "yes":
                    if Gameplay.bot_flag == False:
                        TypeOfGame.right_questions_player += 1
                    else:
                        TypeOfGame.right_questions_opponent += 1
                        
                    
                    user_available_players = [player for player in user_available_players if player.position.lower() == selected_position.lower()]
                else:
                    
                    user_available_players = [player for player in user_available_players if player.position.lower() != selected_position.lower()]

                # Exibir jogadores disponíveis no continente selecionado
                #print(f"Available players:")
                #for player in user_available_players:
                  #  player.display_info()
                if Gameplay.bot_flag==True:
                    messagebox.showinfo("Opponent number of players", f"The number of players available for the opponent is: {len(user_available_players)}")
                    
            else:
                print("Invalid option. Please select a valid number.")
        
        

        return user_available_players




    
def main():
    global username
    global players_list
    
    checker = UserChecker()
    
    players_list=PhotoPlayer.load_players_from_csv()
    root.destroy()
    user_greeter = UserGreeter()
    user_greeter.greet_user(username)
    
    display_menu(players_list)
    
    #select_team()
    
    

def on_submit():
    global username 
    username = username_entry.get()
    main()
    root.quit()

root = tk.Tk()
root.title("Username Entry")
root.state('zoomed')

# Carregar a imagem
image_path = os.path.join('logos', 'intro.png')  # Ajuste o caminho conforme necessário
image = Image.open(image_path)
photo = ImageTk.PhotoImage(image)

# Criando um frame para centralizar o conteúdo
frame = tk.Frame(root)
frame.pack(expand=True)

# Adicionando a imagem ao frame
image_label = tk.Label(frame, image=photo)
image_label.pack()

tk.Label(frame, text="Enter the username:").pack()

username_entry = tk.Entry(frame)
username_entry.pack()

submit_button = tk.Button(frame, text="Submit", command=on_submit)
submit_button.pack()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
    
    
#if __name__ == "__main__":
#    main()
