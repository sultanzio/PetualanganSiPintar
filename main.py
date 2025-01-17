import random
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.uix.button import Button
from kivy.properties import BooleanProperty, NumericProperty
from kivy.core.audio import SoundLoader
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock

class MainMenuScreen(Screen): pass
class LevelSelectionScreen(Screen): pass
class SettingsScreen(Screen): pass
class AboutScreen(Screen): pass
class PuzzleScreen(Screen): pass
class MultipleChoiceScreen(Screen): pass
class LevelBossScreen(Screen): pass

class PetualanganApp(App):
    sound_on = BooleanProperty(True)
    music_on = BooleanProperty(True)
    sfx_volume = NumericProperty(0.5)
    music_volume = NumericProperty(0.5)

    current_level = NumericProperty(1)
    current_question_index = NumericProperty(0)
    score = NumericProperty(0)
    highest_level_completed = NumericProperty(0)

    store_progress = None
    store_settings = None

    click_sound = None
    correct_sound = None
    incorrect_sound = None
    win_sound = None
    lose_sound = None
    bg_music = None

    timer_event = None
    timer_value = NumericProperty(20)

    questions_data = {}

    puzzle_tiles = [
        "assets/puzzle_0.png", "assets/puzzle_1.png", "assets/puzzle_2.png",
        "assets/puzzle_3.png", "assets/puzzle_4.png", "assets/puzzle_5.png",
        "assets/puzzle_6.png", "assets/puzzle_7.png", "assets/puzzle_empty.png"
    ]
    puzzle_order = []
    empty_index = 8

    def build(self):
        Builder.load_file('petualangan.kv')
        self.sm = self.root
        self.sm.transition = FadeTransition()

        self.store_progress = JsonStore('progress.json')
        self.store_settings = JsonStore('settings.json')

        self.load_questions()
        self.load_sounds()
        self.load_settings_from_store()

        if self.store_progress.exists('progress'):
            saved = self.store_progress.get('progress')
            self.highest_level_completed = saved.get('highest_level_completed', 0)

        self.play_bg_music()
        return self.sm

    def load_questions(self):
        try:
            with open('questions.json', 'r', encoding='utf-8') as f:
                self.questions_data = json.load(f)
        except:
            self.questions_data = {}

    def load_sounds(self):
        self.click_sound = SoundLoader.load('assets/click.wav')
        self.correct_sound = SoundLoader.load('assets/correct.wav')
        self.incorrect_sound = SoundLoader.load('assets/incorrect.wav')
        self.win_sound = SoundLoader.load('assets/win.wav')
        self.lose_sound = SoundLoader.load('assets/lose.wav')
        self.bg_music = SoundLoader.load('assets/bg_music.mp3')
        if self.bg_music:
            self.bg_music.loop = True

    def setup_puzzle_screen(self):
        screen = self.sm.get_screen('puzzle')
        puzzle_score_label = screen.ids.puzzle_score_label
        puzzle_instruction_label = screen.ids.puzzle_instruction_label
        puzzle_grid = screen.ids.puzzle_grid

        puzzle_score_label.text = f"Skor: {self.score}"
        puzzle_instruction_label.text = "Susun puzzle di bawah"

        self.puzzle_order = self.puzzle_tiles[:]
        random.shuffle(self.puzzle_order)
        self.empty_index = self.puzzle_order.index("assets/puzzle_empty.png")

        puzzle_grid.clear_widgets()
        for i, tile_source in enumerate(self.puzzle_order):
            btn = Button(background_normal=tile_source,
                         background_down=tile_source,
                         size_hint=(None, None),
                         size=(dp(100), dp(100)))
            btn.bind(on_release=lambda w, idx=i: self.tile_pressed(idx))
            puzzle_grid.add_widget(btn)

    def tile_pressed(self, idx):
        if idx == self.empty_index: return
        row_empty, col_empty = divmod(self.empty_index, 3)
        row_tile, col_tile = divmod(idx, 3)
        if abs(row_empty - row_tile) + abs(col_empty - col_tile) == 1:
            self.puzzle_order[self.empty_index], self.puzzle_order[idx] = \
                self.puzzle_order[idx], self.puzzle_order[self.empty_index]
            self.empty_index = idx
            self.refresh_puzzle_grid()
            self.play_click_sound()

    def refresh_puzzle_grid(self):
        screen = self.sm.get_screen('puzzle')
        puzzle_grid = screen.ids.puzzle_grid
        puzzle_grid.clear_widgets()
        for i, tile_source in enumerate(self.puzzle_order):
            btn = Button(background_normal=tile_source,
                         background_down=tile_source,
                         size_hint=(None, None),
                         size=(dp(100), dp(100)))
            btn.bind(on_release=lambda w, idx=i: self.tile_pressed(idx))
            puzzle_grid.add_widget(btn)

    def reset_puzzle(self):
        self.play_click_sound()
        self.setup_puzzle_screen()

    def check_puzzle_solved(self):
        if self.puzzle_order == self.puzzle_tiles:
            self.play_correct_sound()
            self.score += 10
            if self.highest_level_completed < 1:
                self.highest_level_completed = 1
            self.store_progress.put('progress',
                                    level=self.current_level,
                                    score=self.score,
                                    highest_level_completed=self.highest_level_completed)
            self.load_next_level()
        else:
            self.play_incorrect_sound()
            print("Puzzle belum benar, coba lagi.")

    def show_puzzle_solution(self):
        self.puzzle_order = self.puzzle_tiles[:]
        self.empty_index = self.puzzle_order.index("assets/puzzle_empty.png")
        self.refresh_puzzle_grid()
        self.play_click_sound()

    def load_multiplechoice_question(self):
        screen = self.sm.get_screen('multiple_choice')
        score_label = screen.ids.score_label
        timer_label = screen.ids.timer_label
        question_label = screen.ids.question_label
        options_layout = screen.ids.options_layout
        mc_hint_label = screen.ids.mc_hint_label

        score_label.text = f"Skor: {self.score}"
        mc_hint_label.text = ""

        options_layout.clear_widgets()

        if 'level2' not in self.questions_data:
            question_label.text = "Soal Level 2 tidak tersedia."
            return

        if self.current_question_index >= len(self.questions_data['level2']):
            self.load_next_level()
            return

        q_data = self.questions_data['level2'][self.current_question_index]
        question_label.text = q_data.get('question', 'Pertanyaan...')
        options = q_data.get('options', [])
        hint_text = q_data.get('hint', "")

        for i, opt in enumerate(options):
            btn = Button(text=opt, size_hint=(None, None), size=(dp(380), dp(40)))
            btn.bind(on_release=lambda w, idx=i, hint=hint_text: self.check_mc_answer(idx, hint))
            options_layout.add_widget(btn)

    def check_mc_answer(self, chosen_index, hint):
        q_data = self.questions_data['level2'][self.current_question_index]
        correct_index = q_data.get('correct_index', 0)
        screen = self.sm.get_screen('multiple_choice')
        mc_hint_label = screen.ids.mc_hint_label

        if chosen_index == correct_index:
            self.play_correct_sound()
            self.score += 10
            mc_hint_label.text = ""
        else:
            self.play_incorrect_sound()
            self.timer_value -= 3
            mc_hint_label.text = f"Jawaban Salah!\nHINT: {hint if hint else '-'}"

        self.current_question_index += 1
        self.load_multiplechoice_question()

    def load_boss_question(self):
        screen = self.sm.get_screen('boss_level')
        boss_score_label = screen.ids.boss_score_label
        boss_timer_label = screen.ids.boss_timer_label
        boss_question_label = screen.ids.boss_question_label
        boss_options_layout = screen.ids.boss_options_layout
        boss_hint_label = screen.ids.boss_hint_label
        boss_health_bar = screen.ids.boss_health_bar

        boss_score_label.text = f"Skor: {self.score}"
        boss_hint_label.text = ""
        boss_options_layout.clear_widgets()

        if 'level3' not in self.questions_data:
            boss_question_label.text = "Soal Level 3 tidak ada."
            return

        if self.current_question_index >= len(self.questions_data['level3']):
            # Jika boss belum dikalahkan saat pertanyaan habis, kalah
            if boss_health_bar.value > 0:
                print("Boss belum kalah. Anda kalah!")
                self.show_lose_popup()
            self.go_to_main_menu()
            return

        q_data = self.questions_data['level3'][self.current_question_index]
        boss_question_label.text = q_data.get('question', 'Pertanyaan Bos...')
        options = q_data.get('options', [])
        hint_text = q_data.get('hint', "")

        for i, opt_text in enumerate(options):
            btn = Button(text=opt_text, size_hint=(None, None), size=(dp(380), dp(40)))
            btn.bind(on_release=lambda w, idx=i, hint=hint_text: self.check_boss_answer(idx, hint))
            boss_options_layout.add_widget(btn)

    def check_boss_answer(self, chosen_index, hint):
        screen = self.sm.get_screen('boss_level')
        boss_health_bar = screen.ids.boss_health_bar
        boss_hint_label = screen.ids.boss_hint_label

        q_data = self.questions_data['level3'][self.current_question_index]
        correct_index = q_data.get('correct_index', 0)

        if chosen_index == correct_index:
            self.play_correct_sound()
            boss_health_bar.value -= 20
            self.score += 20
            boss_hint_label.text = ""
            if boss_health_bar.value <= 0:
                print("Bos Kalah! Menang!")
                self.show_win_popup()
                self.go_to_main_menu()
                return
        else:
            self.play_incorrect_sound()
            self.timer_value -= 3
            boss_hint_label.text = f"Jawaban Salah!\nHINT: {hint if hint else '-'}"

        self.current_question_index += 1
        self.load_boss_question()

    def start_new_game(self):
        self.play_click_sound()
        self.current_level = 1
        self.score = 0
        self.current_question_index = 0
        self.highest_level_completed = 0
        self.store_progress.put('progress',
                                level=self.current_level,
                                score=self.score,
                                highest_level_completed=self.highest_level_completed)
        self.go_to_level(1)

    def handle_continue_game(self):
        self.play_click_sound()
        if self.store_progress.exists('progress'):
            saved = self.store_progress.get('progress')
            self.current_level = saved.get('level', 1)
            self.score = saved.get('score', 0)
            self.highest_level_completed = saved.get('highest_level_completed', 0)
            self.current_question_index = 0
            self.go_to_level(self.current_level)
        else:
            self.start_new_game()

    def open_settings(self):
        self.play_click_sound()
        self.sm.current = 'settings'

    def show_about(self):
        self.play_click_sound()
        about_screen = self.sm.get_screen('about')
        about_screen.ids.about_text.text = (
            "Game Petualangan Si Pintar.\n"
            "Level 1: Puzzle (Check, Reset, Tampilkan Solusi)\n"
            "Level 2,3: Jawaban langsung dicek + HINT.\n"
            "Timer pakai background timer_bg.\n"
            "Pertanyaan warna hitam.\n"
            "Selamat Bermain!"
        )
        self.sm.current = 'about'

    def go_to_main_menu(self):
        self.play_click_sound()
        self.stop_timer()
        self.sm.current = 'main_menu'

    def go_to_level_selection(self):
        self.play_click_sound()
        self.stop_timer()
        self.sm.current = 'level_selection'

    def go_to_level(self, level_number):
        self.play_click_sound()
        self.stop_timer()
        if level_number > self.highest_level_completed + 1:
            self.show_popup(f"Anda harus menyelesaikan Level {self.highest_level_completed + 1} terlebih dahulu!")
            return
        self.current_level = level_number
        self.store_progress.put('progress',
                                level=self.current_level,
                                score=self.score,
                                highest_level_completed=self.highest_level_completed)
        self.current_question_index = 0
        if level_number == 1:
            self.sm.current = 'puzzle'
            self.setup_puzzle_screen()
        elif level_number == 2:
            self.sm.current = 'multiple_choice'
            self.load_multiplechoice_question()
            self.start_timer()
        elif level_number == 3:
            self.sm.current = 'boss_level'
            self.load_boss_question()
            self.start_timer()

    def load_next_level(self):
        self.play_click_sound()
        next_level = self.current_level + 1
        if self.current_level > self.highest_level_completed:
            self.highest_level_completed = self.current_level
        self.store_progress.put('progress',
                                level=self.current_level,
                                score=self.score,
                                highest_level_completed=self.highest_level_completed)
        if next_level > 3:
            print("Selesai! Kembali ke menu.")
            self.go_to_main_menu()
        else:
            self.go_to_level(next_level)

    def start_timer(self):
        self.timer_value = 20
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def update_timer(self, dt):
        self.timer_value -= 1
        if self.current_level == 2:
            screen = self.sm.get_screen('multiple_choice')
            timer_label = screen.ids.timer_label
            timer_label.text = f"Waktu: {self.timer_value}"
            timer_label.color = (1,0,0,1) if self.timer_value <= 5 else (1,1,1,1)
        elif self.current_level == 3:
            screen = self.sm.get_screen('boss_level')
            boss_timer_label = screen.ids.boss_timer_label
            boss_timer_label.text = f"Waktu: {self.timer_value}"
            boss_timer_label.color = (1,0,0,1) if self.timer_value <= 5 else (1,1,1,1)
        if self.timer_value <= 0:
            print("Waktu habis!")
            self.stop_timer()
            self.show_lose_popup()
            self.go_to_main_menu()

    def show_win_popup(self):
        from kivy.uix.popup import Popup
        from kivy.uix.image import Image
        popup = Popup(title='Selamat!',
                      content=Image(source='assets/win.png'),
                      size_hint=(None, None),
                      size=(400, 400))
        popup.open()
        if self.win_sound:
            self.win_sound.play()

    def show_lose_popup(self):
        from kivy.uix.popup import Popup
        from kivy.uix.image import Image
        popup = Popup(title='Maaf!',
                      content=Image(source='assets/lose.png'),
                      size_hint=(None, None),
                      size=(400, 400))
        popup.open()
        if self.lose_sound:
            self.lose_sound.play()

    def play_bg_music(self):
        if self.bg_music and self.music_on:
            self.bg_music.volume = self.music_volume
            self.bg_music.play()

    def stop_bg_music(self):
        if self.bg_music:
            self.bg_music.stop()

    def update_bg_music_volume(self):
        if self.bg_music:
            self.bg_music.volume = self.music_volume
            if self.music_on:
                if self.bg_music.state != 'play':
                    self.bg_music.play()
            else:
                self.bg_music.stop()

    def play_click_sound(self):
        if self.sound_on and self.click_sound:
            self.click_sound.volume = self.sfx_volume
            self.click_sound.play()

    def play_correct_sound(self):
        if self.sound_on and self.correct_sound:
            self.correct_sound.volume = self.sfx_volume
            self.correct_sound.play()

    def play_incorrect_sound(self):
        if self.sound_on and self.incorrect_sound:
            self.incorrect_sound.volume = self.sfx_volume
            self.incorrect_sound.play()

    def show_popup(self, message):
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        popup = Popup(title='Peringatan',
                      content=Label(text=message),
                      size_hint=(None, None),
                      size=(400, 200))
        popup.open()

    def load_settings_from_store(self):
        if self.store_settings.exists('config'):
            config = self.store_settings.get('config')
            self.sound_on = config.get('sound_on', True)
            self.music_on = config.get('music_on', True)
            self.sfx_volume = config.get('sfx_volume', 0.5)
            self.music_volume = config.get('music_volume', 0.5)
        self.update_bg_music_volume()

    def save_settings(self):
        self.play_click_sound()
        settings_screen = self.sm.get_screen('settings')
        vol_sfx = settings_screen.ids.volume_sfx_slider.value
        vol_music = settings_screen.ids.volume_music_slider.value
        self.sfx_volume = vol_sfx
        self.music_volume = vol_music
        self.sound_on = (self.sfx_volume > 0)
        self.music_on = (self.music_volume > 0)
        self.store_settings.put('config',
                                sound_on=self.sound_on,
                                music_on=self.music_on,
                                sfx_volume=self.sfx_volume,
                                music_volume=self.music_volume)
        self.update_bg_music_volume()
        self.go_to_main_menu()

if __name__ == '__main__':
    PetualanganApp().run()
