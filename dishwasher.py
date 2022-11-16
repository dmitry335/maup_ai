from tkinter import *
from tkinter import ttk
import random

global timer

# settings
UPDATE_TIME = 1.5
DISH_RANGE_ONE_TABLE = (5, 25)
SHOW_TRIGGER_TIME = 1500

DISHES_TOTAL = 400                  # кількість посуду всього
DISHWASHER_MAX_DISHES = 100         # максимальна ємність посудомийки
DISHES_REQUIRED_MIN_PERCENT = 20    # мінімально допустима кількість чистого посуду


class myGUI:
    def __init__(self, parent):
        # root window
        self.root = Tk()
        self.root.title('DishWasher')
        self.root.resizable(False, False)
        self.root.config(bg='#000000', padx=30, pady=30)

        self.frame_settings = Frame(self.root, bg='black')
        self.frame_settings.grid(column=0, row=1)
        self.frame_settings.grid()

        self.frame_top = Frame(self.root, bg='black')
        self.frame_top.grid(column=0, row=2)
        self.frame_top.grid()

        self.frame_bottom = Frame(self.root, bg='black')
        self.frame_bottom.grid(column=0, row=3, pady=(10, 0))

        self.s = ttk.Style()
        self.s.theme_use('clam')

        self.s.configure("Horizontal.TProgressbar",
                         foreground='white',
                         background='white',
                         troughcolor='black',
                         bordercolor='white',
                         )
        self.s.configure("text_top.TLabel",
                         font=("Arial", 17),
                         foreground='white',
                         background='black',
                         )
        self.s.configure("nums.TLabel",
                         font=("Arial Bold", 50),
                         foreground='white',
                         background='black',
                         )
        self.s.configure("nums_trigger.TLabel",
                         font=("Arial Bold", 50),
                         foreground='red',
                         background='black',
                         )
        self.s.configure("TButton",
                         font=("Arial Bold", 20),
                         foreground='white',
                         background='black',
                         )

        self.s.map('TButton', foreground=[('active', '!disabled', 'black')],
                   background=[('active', 'white')])

        # labels
        ttk.Label(self.frame_top, style="text_top.TLabel", text="Посуд чистий").grid(column=0, row=0, padx=10,
                                                                                     pady=(0, 8))

        ttk.Label(self.frame_top, style="text_top.TLabel", text="Заповненість посудомийки").grid(column=2, row=0,
                                                                                                 padx=10,
                                                                                                 pady=(0, 8))
        self.lbl_dishes_clean = ttk.Label(self.frame_top, style="nums.TLabel", text="")
        self.lbl_dishes_clean.grid(column=0, row=2, padx=10, pady=(5, 0))
        self.lbl_dishwasher_fill = ttk.Label(self.frame_top, style="nums.TLabel", text="")
        self.lbl_dishwasher_fill.grid(column=2, row=2, padx=10, pady=(5, 0))

        # progressbar
        self.pb_dishes_clean = ttk.Progressbar(
            self.frame_top,
            style="Horizontal.TProgressbar",
            orient='horizontal',
            mode='determinate',
            length=240,
            value=100,
        )
        self.s.configure('pb_dishes_clean', foreground='maroon')

        self.pb_dishwasher_fill = ttk.Progressbar(
            self.frame_top,
            style="TProgressbar",
            orient='horizontal',
            mode='determinate',
            length=240,
            value=0,
        )
        self.pb_dishes_clean.grid(column=0, row=1, padx=10, pady=0)
        self.pb_dishwasher_fill.grid(column=2, row=1, padx=10, pady=0)

        # start button
        self.start_button = ttk.Button(
            self.frame_bottom,
            style='TButton',
            text='Старт',
            command=parent.start
        )
        self.start_button.grid(column=0, row=3, padx=10, pady=10, sticky=E)

        # stop button
        self.stop_button = ttk.Button(
            self.frame_bottom,
            style='TButton',
            text='Сброс',
            command=self.reset
        )
        self.stop_button.grid(column=1, row=3, padx=10, pady=10, sticky=W)

        self.root.mainloop()

    def clear_triggered(self):
        # вимикаємо сповіщення, яка умова вімкнула посудомийку
        self.lbl_dishes_clean.configure(style='nums.TLabel')
        self.lbl_dishwasher_fill.configure(style='nums.TLabel')

    def set_clear_timer(self):
        # встановлюємо таймер для методу вимкнення сповіщення про вмикання посудомийки
        self.root.after(1500, self.clear_triggered)

    def show_trigger_low_dishes(self):
        # показуємоє, що посудомийка увімкнулась через низьку кількість наявних чистих тарілок
        self.lbl_dishes_clean.configure(style='nums_trigger.TLabel')
        self.set_clear_timer()

    def show_trigger_full_dishwasher(self):
        # показуємо, що посудомийка увімкнулась тому, що була повністю заповнена
        self.lbl_dishwasher_fill.configure(style='nums_trigger.TLabel')
        self.set_clear_timer()

    def reset(self):
        # зупиняємось і повертаємось до початкового стану
        self.pb_dishes_clean["value"] = 100
        self.pb_dishwasher_fill["value"] = 0

        self.lbl_dishes_clean.config(text=int(DISHES_TOTAL))
        self.lbl_dishwasher_fill.config(text=int(0))

    def udpate_dishes_clean(self, __dishes_clean):
        self.pb_dishes_clean["value"] = 100 * __dishes_clean / DISHES_TOTAL
        self.lbl_dishes_clean.config(text=int(__dishes_clean))

    def update_dishes_in_dishwasher(self, __dishes_in_dishwasher):
        self.pb_dishwasher_fill["value"] = __dishes_in_dishwasher * 100 / DISHWASHER_MAX_DISHES
        self.lbl_dishwasher_fill.config(text=int(__dishes_in_dishwasher))


class DishWasher(myGUI):
    def __init__(self):
        self.running = False
        self.timer = None
        self.dishes_in_use = 0
        self.dishes_in_dishwasher = 0
        super().__init__(self)

    def wash(self, dishes_left=0):
        self.dishes_in_dishwasher = dishes_left
        self.update_all()

    def start(self):
        if not self.running:
            self.running = True
            self.one_cycle()

    def one_cycle(self):
        self.update_all()
        # кількість тарілок для нових замовлень відвідувачам
        new_order_dishes = random.randint(DISH_RANGE_ONE_TABLE[0], DISH_RANGE_ONE_TABLE[1])
        # кількість брудних тарілок, які відправляються в посудомийку
        new_dirty_dishes = random.randint(DISH_RANGE_ONE_TABLE[0], DISH_RANGE_ONE_TABLE[1])
        if new_dirty_dishes > self.dishes_in_use:
            new_dirty_dishes = self.dishes_in_use
        print("new dishes = ", new_order_dishes, "   new dirty dishes = ", new_dirty_dishes)

        # беремо чисті тарілки на нові замовлення
        self.dishes_in_use += new_order_dishes
        # звільнені тарілки відправляємо в посудомийку
        self.dishes_in_dishwasher += new_dirty_dishes
        self.dishes_in_use -= new_dirty_dishes

        # якщо заповнилась вся посудомийка
        if self.dishes_in_dishwasher >= DISHWASHER_MAX_DISHES:
            # якщо посуду більше ємності посудомийки миєм скільки влізло, залишок складуємо в "брудне"
            self.wash(self.dishes_in_dishwasher - DISHWASHER_MAX_DISHES)
            self.show_trigger_full_dishwasher()
            print("dishwasher is full - washing")

        # якщо залишилось меньше DISHES_REQUIRED_MIN_PERCENT відсотків вільного посуду вмикаємо посудомийку
        if DISHES_TOTAL - self.dishes_in_use - self.dishes_in_dishwasher < DISHES_TOTAL / 100 * DISHES_REQUIRED_MIN_PERCENT:
            self.wash()
            self.show_trigger_low_dishes()
            print("free dishes is low, washing")

        self.timer = self.root.after(500, self.one_cycle)

    def update_all(self):
        self.update_dishes_in_dishwasher(self.dishes_in_dishwasher)
        self.udpate_dishes_clean(DISHES_TOTAL - self.dishes_in_use - self.dishes_in_dishwasher)
        print("free = ", DISHES_TOTAL - self.dishes_in_use - self.dishes_in_dishwasher, "  in use = ",
              self.dishes_in_use, "   in washer = ", self.dishes_in_dishwasher)

    def reset(self):
        if self.running:
            self.root.after_cancel(self.timer)
            self.running = False
        self.dishes_in_use = 0
        self.dishes_in_dishwasher = 0
        self.update_all()


def main():
    DishWasher()


if __name__ == "__main__":
    main()
