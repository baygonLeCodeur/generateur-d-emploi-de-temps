from fpdf import FPDF
class LesEmploisDeTpsClasses(FPDF):
    def __init__(self, orientation="P", unit="mm", format="A4"): 
        super().__init__(orientation, unit, format)
        self.horaires = ["Matin 1", "Matin 2", "Matin 3", "Matin 4", "Matin 5", "Soir 1", "Soir 2", "Soir 3", "Soir 4", "Soir 5"]
    def rediger_edt(self, classe, emploi_du_temps):
        decal_v = 30
        self.add_page()
        self.set_margins(5, 5)
        self.set_font("helvetica", "B", 10)
        self.set_xy(15, 15)
        self.cell(w=180, h=5, txt=classe, border=0, align="C")
        self.set_xy(15, decal_v)
        for plage_h in self.horaires:
            self.multi_cell(w=30, h=5, txt=f"\n{plage_h}\n\n", border=1, align="L")
            decal_v += 15
            self.set_xy(15, decal_v)
        decal_h = 45
        for jour in ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]:
            if "Matin" in emploi_du_temps[jour] and "Soir" in emploi_du_temps[jour]:
                pg_jour = emploi_du_temps[jour]["Matin"] + emploi_du_temps[jour]["Soir"]
            elif "Soir" not in emploi_du_temps[jour]:
                pg_jour = emploi_du_temps[jour]["Matin"] + [None, None, None, None, None]
            else:
                pg_jour = [None, None, None, None, None] + emploi_du_temps[jour]["Soir"]
            decal_v = 25
            self.set_xy(decal_h, decal_v)
            self.cell(w=30, h=5, txt=jour, border=1, align="C")
            decal_v = 30
            self.set_xy(decal_h, decal_v)
            for plage_h in pg_jour:
                if plage_h is None:
                    self.multi_cell(w=30, h=5, txt=f"\n\n\n", border=1, align="L")
                else:
                    prof, matiere, salle = plage_h["prof"], plage_h["matiere"], plage_h["salle"]
                    self.multi_cell(w=30, h=5, txt=f"{prof}\n{matiere}\n{salle}", border=1, align="L")
                decal_v += 15
                self.set_xy(decal_h, decal_v)
            decal_h += 30
            self.set_xy(decal_h, decal_v)