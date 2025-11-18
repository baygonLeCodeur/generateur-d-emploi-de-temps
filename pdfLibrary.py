from fpdf import FPDF


class LesEmploisDeTpsClasses(FPDF):
    def __init__(self, orientation="P", unit="mm", format="A4"): 
        super().__init__(orientation, unit, format)
        self.horaires = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10"]
    
    def rediger_edt(self, classe, emploi_du_temps):
        decal_v = 30
        self.add_page()
        self.set_margins(5, 5)
        self.set_font("helvetica", "B", 12)
        self.set_xy(15, 15)
        self.cell(w=180, h=5, txt=f"Emploi du temps - {classe}", border=0, align="C")
        self.set_font("helvetica", "B", 9)
        self.set_xy(15, decal_v)
        for plage_h in self.horaires:
            self.multi_cell(w=30, h=5, txt=f"\n{plage_h}\n\n", border=1, align="C")
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
            self.set_font("helvetica", "B", 10)
            self.cell(w=30, h=5, txt=jour, border=1, align="C")
            decal_v = 30
            self.set_xy(decal_h, decal_v)
            self.set_font("helvetica", "", 8)
            for plage_h in pg_jour:
                if plage_h is None:
                    self.multi_cell(w=30, h=5, txt=f"\n\n\n", border=1, align="L")
                else:
                    prof = plage_h.get("prof", "")
                    matiere = plage_h.get("matiere", "")
                    salle = plage_h.get("salle", "")
                    self.multi_cell(w=30, h=5, txt=f"{matiere}\n{prof}\n{salle}", border=1, align="C")
                decal_v += 15
                self.set_xy(decal_h, decal_v)
            decal_h += 30
            self.set_xy(decal_h, decal_v)


class LesEmploisDeTpsProfs(FPDF):
    def __init__(self, orientation="P", unit="mm", format="A4"): 
        super().__init__(orientation, unit, format)
        self.horaires = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H10"]
    
    def rediger_edt(self, prof_id, prof_nom, emploi_du_temps):
        decal_v = 30
        self.add_page()
        self.set_margins(5, 5)
        self.set_font("helvetica", "B", 12)
        self.set_xy(15, 15)
        titre = f"Emploi du temps - {prof_nom}" if prof_nom else f"Emploi du temps - {prof_id}"
        self.cell(w=180, h=5, txt=titre, border=0, align="C")
        self.set_font("helvetica", "B", 9)
        self.set_xy(15, decal_v)
        for plage_h in self.horaires:
            self.multi_cell(w=30, h=5, txt=f"\n{plage_h}\n\n", border=1, align="C")
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
            self.set_font("helvetica", "B", 10)
            self.cell(w=30, h=5, txt=jour, border=1, align="C")
            decal_v = 30
            self.set_xy(decal_h, decal_v)
            self.set_font("helvetica", "", 8)
            for plage_h in pg_jour:
                if plage_h is None:
                    self.multi_cell(w=30, h=5, txt=f"\n\n\n", border=1, align="L")
                else:
                    classe = plage_h.get("classe", "")
                    salle = plage_h.get("salle", "")
                    self.multi_cell(w=30, h=5, txt=f"\n{classe}\n{salle}", border=1, align="C")
                decal_v += 15
                self.set_xy(decal_h, decal_v)
            decal_h += 30
            self.set_xy(decal_h, decal_v)