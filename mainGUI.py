import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

class KolkoIKrzyzyk:
    def __init__(self, root, rola, ip=None):

        self.licznik = 0
        self.klient = None
        self.serwer = None
        self.zwyciezca = None
        self.koniec_gry = False
        self.rola = rola
        self.plansza = [[" " for _ in range(3)] for _ in range(3)]
        self.tura = "X"
        self.ty = "X"
        self.przeciwnik = "O"
        self.root = root
        self.root.title("Kółko i Krzyżyk")
        self.przyciski = [[None for _ in range(3)] for _ in range(3)]
        self.utworz_plansze()

        if rola == "gospodarz":
            threading.Thread(target=self.hostuj_gre, args=("localhost", 9999)).start()
        elif rola == "klient" and ip:
            threading.Thread(target=self.polacz_z_gra, args=(ip, 9999)).start()

    def utworz_plansze(self):
        for wiersz in range(3):
            for kol in range(3):
                button = tk.Button(self.root, text=" ", font='Arial 20', width=5, height=2,
                                   command=lambda r=wiersz, c=kol: self.przycisk_klikniety(r, c))
                button.grid(row=wiersz, column=kol)
                self.przyciski[wiersz][kol] = button

    def przycisk_klikniety(self, wiersz, kol):
        if self.tura == self.ty and self.plansza[wiersz][kol] == " ":
            ruch = f"{wiersz},{kol}"
            if self.klient:
                try:
                    self.klient.send(ruch.encode('utf-8'))
                except OSError as e:
                    messagebox.showerror("Błąd", f"Błąd wysyłania ruchu: {e}")
            self.zastosuj_ruch([wiersz, kol], self.ty)
            self.tura = self.przeciwnik

    def hostuj_gre(self, host, port):
        self.serwer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serwer.bind((host, port))
        self.serwer.listen(1)

        ip = socket.gethostbyname("localhost")
        self.ip_label = tk.Label(self.root, text=f"IP Gospodarza: {ip}")
        self.ip_label.grid(row=4, columnspan=3)

        self.klient, addr = self.serwer.accept()
        self.ty = "X"
        self.przeciwnik = "O"
        threading.Thread(target=self.obsluga_polaczenia, args=(self.klient,)).start()

    def polacz_z_gra(self, host, port):
        self.klient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.klient.connect((host, port))

        self.ty = 'O'
        self.przeciwnik = 'X'
        threading.Thread(target=self.obsluga_polaczenia, args=(self.klient,)).start()

    def obsluga_polaczenia(self, klient):
        while not self.koniec_gry:
            if self.tura == self.przeciwnik:
                try:
                    dane = klient.recv(1024)
                    if not dane:
                        klient.close()
                        break
                    else:
                        ruch = dane.decode('utf-8')
                        ruch = list(map(int, ruch.split(',')))
                        self.zastosuj_ruch(ruch, self.przeciwnik)
                        self.tura = self.ty
                except OSError as e:
                    messagebox.showerror("Błąd", f"Błąd odbierania danych: {e}")
                    break
        klient.close()

    def zastosuj_ruch(self, ruch, gracz):
        if self.koniec_gry:
            return
        self.licznik += 1
        self.plansza[ruch[0]][ruch[1]] = gracz
        self.przyciski[ruch[0]][ruch[1]].config(text=gracz)
        if self.sprawdz_czy_wygral():
            self.koniec_gry = True
            if self.zwyciezca == self.ty:
                messagebox.showinfo("Koniec Gry", "Wygrałeś!")
            else:
                messagebox.showinfo("Koniec Gry", "Przegrałeś!")

        elif self.licznik == 9:
            self.koniec_gry = True
            messagebox.showinfo("Koniec Gry", "Remis!")

    def sprawdz_czy_wygral(self):
        for wiersz in range(3):
            if self.plansza[wiersz][0] == self.plansza[wiersz][1] == self.plansza[wiersz][2] != " ":
                self.zwyciezca = self.plansza[wiersz][0]
                return True
        for kol in range(3):
            if self.plansza[0][kol] == self.plansza[1][kol] == self.plansza[2][kol] != " ":
                self.zwyciezca = self.plansza[0][kol]
                return True
        if self.plansza[0][0] == self.plansza[1][1] == self.plansza[2][2] != " ":
            self.zwyciezca = self.plansza[0][0]
            return True
        if self.plansza[0][2] == self.plansza[1][1] == self.plansza[2][0] != " ":
            self.zwyciezca = self.plansza[0][2]
            return True
        return False

def wybierz_role(root):
    wybieranie_roli = tk.Toplevel(root)
    wybieranie_roli.title("Wybierz Rolę")

    def wybierz_gospodarza():
        wybieranie_roli.destroy()
        root.deiconify()
        KolkoIKrzyzyk(root, "gospodarz")

    def wybierz_klienta():
        ip = simpledialog.askstring("Informacje Klienta", "Podaj adres IP gospodarza:")
        if ip:
            wybieranie_roli.destroy()
            root.deiconify()
            KolkoIKrzyzyk(root, "klient", ip)
        else:
            messagebox.showerror("Błąd", "Nie podano adresu IP")

    host_button = tk.Button(wybieranie_roli, text="Gospodarz", command=wybierz_gospodarza)
    client_button = tk.Button(wybieranie_roli, text="Klient", command=wybierz_klienta)

    host_button.pack(side="left", padx=20, pady=20)
    client_button.pack(side="right", padx=20, pady=20)

def main():
    root = tk.Tk()
    root.withdraw()

    wybierz_role(root)

    root.mainloop()

if __name__ == "__main__":
    main()
