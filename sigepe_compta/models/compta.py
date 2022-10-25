from odoo import api, models, fields, _, tools
from datetime import date
from odoo.exceptions import UserError, ValidationError, Warning
from num2words import num2words
from unittest import result


class BudgBordMan(models.Model):
    
    _inherit = "budg_bordereau_mandatement_controle_viser"
    
    fictif = fields.Char("fictif")
    
    
class Compta_PC(models.Model): 
    _name = 'compta_prise_charge'
    _rec_name = 'numero_mandat'
    
    etat_mandat = fields.Selection([
        ('T', 'Tout'),
        ('W', 'Mandat Visé')
        ], 'Etat mandat', default = 'T')
    trier_par = fields.Selection([
        ('1', 'N° Ordre'),
        ('d', 'Date'),
        ], 'Trier par')
    numero_mandat = fields.Many2one("budg_mandat", "N° Mandat",domain=[('state', '=', 'O')])
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture', default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'P')]))
    prise_charge_lines = fields.One2many("compta_prise_charge_line", "prise_charge_id", states={'P': [('readonly', True)]})
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération")
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Nature d'opération")
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", required=False)
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1)]", required=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    date_pc = fields.Date("Date", default=fields.Date.context_today, readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('V', 'Validé'),
        ('P', 'Provisoire'),
        ], 'Trier par')
    mnt_total = fields.Integer('Total')
    
    
    
    @api.multi
    def valider_pc(self):
    
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        id_pc = self.id
        val_mandat = str(self.numero_mandat.no_mandat)
        
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("""SELECT sum(montant)
        FROM compta_prise_charge_line WHERE x_exercice_id = %d AND company_id = %d AND prise_charge_id = %d """ %(val_ex, val_struct, id_pc))
        res = self.env.cr.fetchone()
        self.mnt_total = res and res[0]
        val_mnt = self.mnt_total
        
        self.write({'state': 'V'})
    

    
    def remplir_prise(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_mandat = str(self.numero_mandat.id)


        if self.numero_mandat and self.etat_mandat == 'W':
            for vals in self:
                vals.env.cr.execute("""SELECT m.no_eng as eng, m.no_mandat as mandat, l.no_lo as liq, 
                m.dt_etat as dt, m.mnt_ord as mnt, e.cpte_rub as debit, 
                r.souscpte as id_imput_debit, e.cpte_benef as credit, e.imput_benef as id_imput_credit
                from budg_mandat m, budg_engagement e,budg_rubrique br, budg_liqord l, compta_plan_line r
                where m.no_eng = e.no_eng and m.id = %s and r.id = br.no_imputation and 
                br.id = e.cd_rubrique_id and m.no_lo = l.id and m.state = 'O' and m.company_id = %s and m.x_exercice_id = %s""" ,(val_mandat,val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.prise_charge_lines.unlink()
                for line in rows:
                    result.append((0,0, {'num_eng' : line['eng'], 'num_liq': line['liq'], 'num_mandat': line['mandat'], 'date_mandat': line['dt'], 'montant': line['mnt'], 'imp_deb': line['debit'], 'id_imp_deb': line['id_imput_debit'], 'id_imp_cred': line['id_imput_credit'], 'imp_cred': line['credit']}))
                self.prise_charge_lines = result
        elif self.etat_mandat == 'T':
            for vals in self:
                vals.env.cr.execute(""" SELECT distinct m.no_eng as eng, m.no_mandat as mandat, l.no_lo as liq, 
                m.dt_etat as dt, m.mnt_ord as mnt, e.cpte_rub as debit, 
                r.souscpte as id_imput_debit, e.cpte_benef as credit, e.imput_benef as id_imput_credit
                from budg_mandat m, budg_engagement e,budg_rubrique br, budg_liqord l, compta_plan_line r
                where m.no_eng = e.no_eng and r.id = br.no_imputation  and
                br.id = e.cd_rubrique_id and m.no_lo = l.id and m.state = 'O' and m.company_id = %s and m.x_exercice_id = %s""" ,(val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.prise_charge_lines.unlink()
                for line in rows:
                    result.append((0,0, {'num_eng' : line['eng'], 'num_liq': line['liq'], 'num_mandat': line['mandat'], 'date_mandat': line['dt'], 'montant': line['mnt'], 'imp_deb': line['debit'], 'id_imp_deb': line['id_imput_debit'], 'id_imp_cred': line['id_imput_credit'], 'imp_cred': line['credit']}))
                self.prise_charge_lines = result
            
        
        self.write({'state': 'draft'})

    #Fonction compteur et génération des numéros des ecritures et des lignes d'ecritures
    @api.multi
    def generer_ecriture_pc(self):
        
        self.write({'state': 'P'})
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_ecr = self.no_ecr
        id_pc = self.id
        #var_cptesdeb = str(self.prise_charge_lines.id_imp_deb)
        #var_cptescred = str(self.prise_charge_lines.id_imp_cred)              
        #var_deb = str(self.prise_charge_lines.id_imp_deb)
        #var_cred = str(self.prise_charge_lines.imp_cred)
        val_mnt = self.mnt_total
        val_date = str(self.date_pc)
        var_etat = 'P'
        var_sens = 'D' 
        val_mandat = str(self.numero_mandat.no_mandat)
        v_type = int(self.type_ecriture)

        

    #Attribution des numero et lignes d'ecritures pour l'enregistrement des cheques emis 

        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
        
        
        self.env.cr.execute("select id_imp_deb,id_imp_cred from compta_prise_charge_line where x_exercice_id = %d and company_id = %d and prise_charge_id = %d" %(val_ex,val_struct,id_pc))
        val = self.env.cr.dictfetchall()
        var_cptesdebs = val and val[0]['id_imp_deb']
        var_cptesdeb = var_cptesdebs
        var_cptescreds = val and val[0]['id_imp_cred']
        var_cptescred = var_cptescreds
        
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.prise_charge_lines:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_ex,val_struct,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            no_ecrs11 = no_ecrs1 + 1
            no_ecrs1= no_ecrs11
            for record in self.prise_charge_lines:           
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
        for record in self.prise_charge_lines:
            val = (self.no_ecr)
            val_id = (self.id)
            self.env.cr.execute("UPDATE compta_prise_charge_line SET no_ecr = %s WHERE prise_charge_id = %s" ,(val, val_id))
        
        
        self.env.cr.execute("select * from compta_prise_charge where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_pc))
        curs_pc = self.env.cr.dictfetchall()
        no_ecrs = curs_pc and curs_pc[0]['no_ecr']
        no_ecr = int(no_ecrs)
        #typ_jr = curs_paiement and curs_paiement[0]['type_journal']
        
        if self.prise_charge_lines.etat == True:
        
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr,dt_ecriture, type_ecriture, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s,'ID', %s, %s, 'P')" ,(no_ecr,val_date ,v_type, val_ex, val_struct))
            
            var_ecr = self.no_ecr
    
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """ ,(var_ecr, no_ecrs1, var_cptesdeb, val_mnt, val_ex, val_struct, val_date, var_sens, var_etat))
  
            self.env.cr.execute("select * from compta_prise_charge_line where x_exercice_id = %d and company_id = %d and prise_charge_id = %d " %(val_ex, val_struct, id_pc))
            
            for val in self.env.cr.dictfetchall():
                v_ecr = val['no_ecr']
                v_lecr = val['no_lecr']
                v_cred = val['id_imp_cred']
                v_mnt = val['montant']
                v_ex = val['x_exercice_id']
                v_str = val['company_id']
                v_sens = val['fg_sens']
                v_etat = val['fg_etat']
                v_lecr = v_lecr + 1

                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """ ,(v_ecr, v_lecr, v_cred, v_mnt, v_ex, v_str, val_date, v_sens, v_etat))
        
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,v_lecr,val_ex,val_struct))

            
            for line in self.prise_charge_lines:
            
                if self.etat_mandat == "W":
                    self.env.cr.execute("UPDATE budg_mandat SET state = 'E' WHERE no_mandat = %s and x_exercice_id = %s and company_id = %s" ,(val_mandat, val_ex, val_struct,))
                else:
                    self.env.cr.execute("UPDATE budg_mandat SET state = 'E' WHERE state = 'I' and x_exercice_id = %s and company_id = %s" ,(val_ex, val_struct))
        
        else:
            raise validationError(_("Veuillez cochez la case Ok pour la génération d'écriture!"))
        
            
class Compta_PcLine(models.Model):
    _name="compta_prise_charge_line"
    
    no_ecr = fields.Integer()
    no_lecr = fields.Integer("N° Ligne", readonly=True) 
    prise_charge_id = fields.Many2one("compta_prise_charge", ondelete='cascade')
    num_eng = fields.Char("N° Eng", readonly=True)
    num_liq = fields.Char("N° Liq", readonly=True)
    num_mandat = fields.Char("N° Mdt", readonly=True)
    imputation = fields.Char("Imputation", readonly=True)
    date_mandat = fields.Date("Date", readonly=True)
    montant = fields.Integer("Montant", readonly=True)  
    imp_deb = fields.Char("Imput.Débit", readonly=True)
    id_imp_deb = fields.Integer("id Imput.Débit", readonly=True)
    imp_cred = fields.Char("Imput.Crédit", readonly=True)
    id_imp_cred = fields.Integer("id Imput.crédit", readonly=True)
    fg_sens = fields.Char(default = 'C')
    fg_etat = fields.Char(default = 'P')
    etat = fields.Boolean("OK", default = False)
    #active = fields.Boolean(string="Ok ?", default=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
  

class BudgBordRec(models.Model):
    
    _inherit = "budg_bord_titre_recette"
    
    fictif = fields.Char("fictif")
    
class Compta_PCREC(models.Model): 
    _name = 'compta_prise_charge_rec'
    _rec_name = 'numero_titre'
    
    numero_titre = fields.Many2one("budg_titrerecette", "N° Titre Recette", domain=[('et_doss', '=', 'I')])
    etat_titre = fields.Selection([
        ('T', 'Tout'),
        ('W', 'Titre Visé')
        ], 'Etat titre', default = 'T')
    prise_charge_lines = fields.One2many("compta_prise_charge_line_rec", "prise_charge_id", states={'P': [('readonly', True)]})
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture', default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'P')]))
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", required=False)
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1)]", required=False)
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération")
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Nature d'opération")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    date_pc = fields.Date("Date de prise en charge", default=fields.Date.context_today, readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('V', 'Validé'),
        ('P', 'Provisoire'),
        ], 'Trier par')
    mnt_total = fields.Integer('Total')
    
    
    @api.multi
    def valider_pc(self):
    
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        id_pc = self.id
        val_titre = str(self.numero_titre.cd_titre_recette)
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        self.env.cr.execute("""SELECT sum(montant)
        FROM compta_prise_charge_line_rec WHERE x_exercice_id = %d AND company_id = %d AND prise_charge_id = %d """ %(val_ex, val_struct, id_pc))
        res = self.env.cr.fetchone()
        self.mnt_total = res and res[0]
        val_mnt = self.mnt_total
        
        self.write({'state': 'V'})
    

    
    def remplir_prise(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_titre = str(self.numero_titre.cd_titre_recette)

        if self.numero_titre and self.etat_titre == "W":
            for vals in self:
                vals.env.cr.execute("""SELECT t.cd_titre_recette as titre, 
                concat((t.titre_id) ,'-',(t.section_id),'-',(t.chapitre_id),'-',(t.article_id),'-',
                (t.paragraphe_id),'-',t.rubrique_id) as imputation, t.dt_rec as dt, t.mnt_rec as mnt, t.no_imputation as credit, t.no_imput as id_imput_credit, 
                t.imput as id_imput_debit, concat(s.souscpte,' ',s.lb_long) as debit
                from  budg_titrerecette t,budg_rubrique br,compta_plan_line r, ref_souscompte s,  ref_typecontribuable b where t.cd_titre_recette = %s
                and r.id = b.cpte_client and s.id = r.souscpte
                and t.cd_type_contribuable = b.id and br.id = t.cd_rubrique_id and t.company_id = %s and t.x_exercice_id = %s""" ,(val_titre,val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.prise_charge_lines.unlink()
                for line in rows:
                    result.append((0,0, {'num_titre' : line['titre'], 'imputation': line['imputation'], 'date_titre': line['dt'], 'montant': line['mnt'], 'imp_deb': line['debit'], 'id_imp_deb': line['id_imput_debit'], 'id_imp_cred': line['id_imput_credit'], 'imp_cred': line['credit']}))
                self.prise_charge_lines = result
        else:
            for vals in self:
                vals.env.cr.execute("""SELECT t.cd_titre_recette as titre, 
                concat((t.titre_id) ,'-',(t.section_id),'-',(t.chapitre_id),'-',(t.article_id),'-',
                (t.paragraphe_id),'-',t.rubrique_id) as imputation, t.dt_rec as dt, t.mnt_rec as mnt, t.no_imputation as credit, t.no_imput as id_imput_credit, 
                t.imput as id_imput_debit, concat(s.souscpte,' ',s.lb_long) as debit
                from  budg_titrerecette t,budg_rubrique br,compta_plan_line r, ref_souscompte s,  ref_typecontribuable b where
                r.id = b.cpte_client and s.id = r.souscpte
                and t.cd_type_contribuable = b.id and br.id = t.cd_rubrique_id and t.company_id = %s and t.x_exercice_id = %s""" ,(val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.prise_charge_lines.unlink()
                for line in rows:
                    result.append((0,0, {'num_titre' : line['titre'], 'imputation': line['imputation'], 'date_titre': line['dt'], 'montant': line['mnt'], 'imp_deb': line['debit'], 'id_imp_deb': line['id_imput_debit'], 'id_imp_cred': line['id_imput_credit'], 'imp_cred': line['credit']}))
                self.prise_charge_lines = result
        
        self.write({'state': 'draft'})

    #Fonction compteur et génération des numéros des ecritures et des lignes d'ecritures
    @api.multi
    def generer_ecriture_pc(self):
        
        self.write({'state': 'P'})
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_ecr = self.no_ecr
        id_pc = self.id
        #var_cptesdeb = str(self.prise_charge_lines.id_imp_deb)
        #var_cptescred = str(self.prise_charge_lines.id_imp_cred)              
        #var_deb = str(self.prise_charge_lines.id_imp_deb)
        #var_cred = str(self.prise_charge_lines.imp_cred)
        val_mnt = self.mnt_total
        val_date = str(self.date_pc)
        var_etat = 'P'
        var_sens = 'C' 
        val_titre = str(self.numero_titre.cd_titre_recette)
        v_type = int(self.type_ecriture)
        

    #Attribution des numero et lignes d'ecritures pour l'enregistrement des cheques emis 

        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
        
        
        self.env.cr.execute("select id_imp_deb,id_imp_cred from compta_prise_charge_line_rec where x_exercice_id = %d and company_id = %d and prise_charge_id = %d" %(val_ex,val_struct,id_pc))
        val = self.env.cr.dictfetchall()
        var_cptesdeb = val and val[0]['id_imp_deb']
        var_cptescred = val and val[0]['id_imp_cred']
       
        
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.prise_charge_lines:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_ex, val_struct,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            no_ecrs11 = no_ecrs1 + 1
            no_ecrs1= no_ecrs11
            for record in self.prise_charge_lines:           
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
        self.env.cr.execute("select * from compta_prise_charge_rec where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_pc))
        curs_pc = self.env.cr.dictfetchall()
        no_ecrs = curs_pc and curs_pc[0]['no_ecr']
        no_ecr = int(no_ecrs)
        #typ_jr = curs_paiement and curs_paiement[0]['type_journal']
        
        for record in self.prise_charge_lines:
            val = (self.no_ecr)
            val_id = (self.id)
            self.env.cr.execute("UPDATE compta_prise_charge_line_rec SET no_ecr = %s WHERE prise_charge_id = %s" ,(val, val_id))
        
        if self.prise_charge_lines.etat == True:
        
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, 'ID', %s, %s, 'P')" ,(no_ecr, val_date, v_type, val_ex, val_struct))
    
            self.env.cr.execute("select * from compta_prise_charge_line_rec where x_exercice_id = %d and company_id = %d and prise_charge_id = %d " %(val_ex, val_struct, id_pc))
            curs_pec = self.env.cr.dictfetchall()
            
            var_ecr = self.no_ecr
    
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """ ,(var_ecr, no_ecrs1, var_cptesdeb, val_mnt, val_ex, val_struct, val_date, var_sens, var_etat))
            
            self.env.cr.execute("SELECT * FROM compta_prise_charge_line_rec WHERE x_exercice_id = %d AND company_id = %d AND prise_charge_id = %d" %(val_ex, val_struct, id_pc))
            for val in self.env.cr.dictfetchall():
                v_ecr = val['no_ecr']
                v_lecr = val['no_lecr']
                v_cred = val['id_imp_cred']
                v_mnt = val['montant']
                v_ex = val['x_exercice_id']
                v_str = val['company_id']
                v_sens = val['fg_sens']
                v_etat = val['fg_etat']
                v_lecr = v_lecr + 1

                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """ ,(v_ecr, v_lecr, v_cred, v_mnt, v_ex, v_str, val_date, v_sens, v_etat))
            
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,v_lecr,val_ex,val_struct))
            self.env.cr.execute("UPDATE budg_titrerecette SET et_doss = 'E' WHERE cd_titre_recette = %s and x_exercice_id = %s and company_id = %s" ,(val_titre, val_ex, val_struct,))

        else:
            raise ValidationError(_("Veuillez cocher la case pour la génération d'écriture"))
    
class Compta_PcLine(models.Model):
    _name="compta_prise_charge_line_rec"
    
    no_ecr = fields.Integer()
    no_lecr = fields.Integer("N° Ligne", readonly=True) 
    prise_charge_id = fields.Many2one("compta_prise_charge_rec", ondelete="cascade")
    num_titre = fields.Char("N° Titre recette", readonly=True)
    imputation = fields.Char("Imputation", readonly=True)
    date_titre = fields.Date("Date", readonly=True)
    montant = fields.Float("Montant", readonly=True)  
    imp_deb = fields.Char("Imput.Débit", readonly=True)
    id_imp_deb = fields.Integer("id Imput.Débit", readonly=True)
    imp_cred = fields.Char("Imput.Crédit", readonly=True)
    id_imp_cred = fields.Integer("id Imput.crédit", readonly=True)
    fg_sens = fields.Char(default = 'D')
    fg_etat = fields.Char(default = 'P')
    etat = fields.Boolean(string="Ok ?", default=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
  

class compta_compte(models.Model):
    
    @api.depends('cpte','lb_long')
    def _concatenate_cpte(self):
        for test in self:
            test.concate_cpte = str(test.cpte)+ "-" +str(test.lb_long)
    
    _name = "compta_compte"
    _rec_name = 'concate_cpte'
    
    concate_cpte = fields.Char(compute="_concatenate_cpte")
    sous_classe = fields.Many2one("budg_sousclasse_pcg", 'Sous classe')
    cpte = fields.Char("Compte", size=3)
    lb_court = fields.Char("Libellé court")
    lb_long = fields.Char("Libellé long")
    active = fields.Boolean('Actif',default=True)
    souscpte_ids = fields.One2many('compta_souscompte', 'cpte_id')
    
    _sql_constraints = [
        ('cpte', 'unique (cpte)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


class compta_souscompte(models.Model):
    
    @api.depends('souscpte','lb_long')
    def _concatenate_souscpte(self):
        for test in self:
            test.concate_souscpte =str(test.souscpte)+ "-" +str(test.lb_long)
    
    _name = "compta_souscompte"
    _rec_name = 'concate_souscpte'
    
    concate_souscpte = fields.Char(compute = '_concatenate_souscpte', store=True)
    cpte_id = fields.Many2one("compta_compte","Compte")
    souscpte = fields.Char("Sous Compte", size=11)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65)
    active = fields.Boolean('Actif',default=True)
    
    _sql_constraints = [
        ('souscpte', 'unique (souscpte)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


class cl_cpt_pcg(models.Model):
    
    @api.depends('cl_cpt_pcg','lb_long')
    def _concatenate_class(self):
        for test in self:
            test.concate_class = str(test.cl_cpt_pcg)+ "-" +str(test.lb_long)


    _name = "budg_classe_pcg"
    _rec_name = 'concate_class'

    concate_class = fields.Char(compute="_concatenate_class")
    cl_cpt_pcg = fields.Char(string="Classe",size=2, required= True)
    name = fields.Char(string="Libellé court", size=25)
    lb_long = fields.Char(string="Libellé long", size=65, required= True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    scl_cpt_pcg_ids = fields.One2many('budg_sousclasse_pcg','cl_cpt_pcg_id', string="Sous compte")


class Scl_cpt_pcg(models.Model):
    
    @api.depends('scl_cpt_pcg','lb_long')
    def _concatenate_sousclass(self):
        for test in self:
            test.concate_sousclass = str(test.scl_cpt_pcg)+ "-" +str(test.lb_long)

    _name = "budg_sousclasse_pcg"
    _rec_name = 'concate_sousclass'
    
    concate_sousclass = fields.Char(compute="_concatenate_sousclass")
    cl_cpt_pcg_id = fields.Many2one("budg_classe_pcg", "Classe")
    scl_cpt_pcg = fields.Char(string="Sous classe",size=2, required= True)
    name = fields.Char(string="Libellé court", size=25)
    lb_long = fields.Char(string="Libellé long", size=65, required= True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
"""     
    
class Compta_TypeOpCptaline(models.Model):
    
    _inherit = "compta_type_op_cpta_line"
    
    no_imputation = fields.Many2one("compta_plan_comptable",'Imputation')
"""    
    
class Compta_Ecriture(models.Model):
    
    _name='compta_ecriture'
    _rec_name = 'no_ecr'
    
    no_ecr = fields.Integer('N° Ecriture', readonly=True)
    no_lecr = fields.Integer()
    dt_ecriture = fields.Date("Date d'écriture",default=fields.Date.context_today, readonly=True)
    type_journal = fields.Many2one('compta_type_journal', 'Type de journal')
    type_ecriture = fields.Many2one('compta_type_ecriture', "Type d'écriture")
    type_op = fields.Char()
    no_journal = fields.Integer()
    dt_valid = fields.Date()
    dt_verif = fields.Date()
    fg_etat = fields.Boolean()
    fg_fiche = fields.Boolean()
    ecriture_libre_ids = fields.One2many('compta_ligne_ecriture', 'ecriture_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Confirmé'),
        ('P', 'Provisoire'),
        ], 'Etat', default='draft', track_visibility='always')
    
        
    
    
    @api.multi
    def gen_draft(self):
         self.write({'state': 'draft'})
         
    @api.multi
    def gen_confirmer(self):
         self.write({'state': 'C'})
        
    #fonction de generation d'ecriture et ligne d'ecriture
    @api.multi
    def gen_ecr_libr(self):
        
        val_ex = int(self.x_exercice_id.id)
        val_struct = int(self.company_id.id)
        
        self.write({'state': 'P'})
        
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
       
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.ecriture_libre_ids:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            for record in self.ecriture_libre_ids:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))

        
        for record in self.ecriture_libre_ids:
            val = (self.no_ecr)
            val_id = (self.id)
            self.env.cr.execute("UPDATE compta_ligne_ecriture SET no_ecr = %s WHERE ecriture_id = %s" ,(val, val_id))

class Compta_compteur_ecr(models.Model):
    
    _name = "compta_compteur_ecr"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    no_ecr = fields.Integer(default = 0)
    no_lecr = fields.Integer(default = 0)



class Compta_Ligne_Ecriture(models.Model):
    
    _name='compta_ligne_ecriture'
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    ecriture_id = fields.Many2one('compta_ecriture',ondelete='cascade')
    no_ecr = fields.Integer()
    no_lecr = fields.Integer("N° Ligne", readonly = True)
    no_cpte = fields.Many2one('ref_souscompte', 'Compte')
    compte = fields.Many2one('compta_plan_line', 'Compte')
    no_souscpte = fields.Many2one('ref_souscompte', 'Compte')
    no_souscptes = fields.Integer()
    nature_id = fields.Many2one('compta_type_ecriture', "Type d'écriture")
    mt_lecr = fields.Float('Montant', required=True)
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),], 'Sens')
    lb_lecr = fields.Char('Motif/Objet',size=65)
    fg_etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Vérifié'),
        ('R', 'Rejété')], 'Etat', default= 'P')
    listnat_id = fields.Many2one("compta_table_listnat", 'Nature')
    no_bord_trsf = fields.Integer()
    dt_valid = fields.Date('Date')
    type_pj = fields.Many2one('compta_piece_line', 'Pièce Just.')
    piece_id = fields.Many2one('ref_piece_justificatives')
    annee_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="An. PJ")
    ref_pj = fields.Char("Ref. PJ")
    no_bord_rep = fields.Integer(size=6)
    ty_bord_rep = fields.Integer()
    g_lettrage = fields.Boolean()
    dt_lettrage = fields.Date()
    dt_verif = fields.Date()
    cd_struc_final = fields.Char('Pour comptable')
    cd_struc_dest = fields.Char()
    fg_gen = fields.Selection([
        ('Y', 'Oui'),
        ('N', 'Non')], 'Etat', default = 'N')
    dt_ligne = fields.Date("Date",default=fields.Date.context_today)
    
    @api.onchange('compte')
    def OnchangeCompte(self):
        
        for record in self:
            if record.compte:
                record.no_souscptes = record.compte.souscpte.id
            


class Compta_TypeOpGuichet(models.Model):
    
    _name = 'compta_type_op_guichet'
    
    type_opcpta_line_id = fields.Many2one("compta_type1_op_cpta", 'Type opération')
    type_opguichet = fields.Char("Type", size =3)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long      ", size=65)
    cd_assign = fields.Char("")
    fg_pa = fields.Boolean()
    fg_term = fields.Boolean()
    listnat_id = fields.Many2one('compta_table_listnat', 'Nature')
    listnat_id_extra = fields.Many2one('compta_table_listnat')
    no_imputation = fields.Char(size=10)
    no_imp_pc = fields.Char(size=10)
    lb_nature = fields.Char(size=15)
    fg_grant_ac = fields.Boolean("Ac")
    fg_grant_ord = fields.Boolean("ORD")
    fg_facial = fields.Boolean()
    fg_guichet = fields.Boolean("G")
    fg_ch_emis = fields.Boolean("C/V")
    fg_op_relev = fields.Boolean("R")
    fg_retenue = fields.Boolean("t")
    col_id = fields.Many2one('compta_colonne_caisse', "Col. brouill caiss")
    typ2_assign = fields.Char(size=3)
    na_fixe = fields.Char(size=10)
    operation_id = fields.Many2one("compta_operation")
    montant_op = fields.Integer('Montant', size=15)
    _sql_constraints = [
        ('type_opguichet', 'unique (type_opguichet)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
   
    

class Reg_OP_Banque_Unique(models.Model):
    _name='compta_reg_op_banque_unique'
    _rec_name = 'type_opbanque'
    
    type1_opcpta_id = fields.Many2one("compta_type1_op_cpta", 'Libellé de type de base', required = True)
    code_base = fields.Char()
    type_opbanque = fields.Many2one("compta_type_op_banque", string="Type opération banque", required = True)
    cpte_cred = fields.Many2one("compta_plan_line", 'Crédit', required = True)
    cred_id = fields.Integer()
    cpte_deb = fields.Many2one("compta_plan_line", 'Débit', required = True)
    deb_id = fields.Integer()
    type_journal = fields.Many2one("compta_type_journal", string="Journal")
    assign = fields.Selection([
        ('Ac', 'AC'),
        ('DAF', 'DAF'),
        ('STRUCT', 'STRUCT'),
        ], 'Assignataire', index=True, copy=False, track_visibility='always')
    lb_comment = fields.Text("Commentaire")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
   

    @api.onchange('cpte_cred')
    def OnchangeCpteCred(self):
        
        for record in self:
            if record.cpte_cred:
                record.cred_id = record.cpte_cred.souscpte.id
    
    @api.onchange('cpte_deb')
    def OnchangeCpteDeb(self):
        
        for record in self:
            if record.cpte_deb:
                record.deb_id = record.cpte_deb.souscpte.id
                
    @api.onchange('type1_opcpta_id')
    def OnchangeType(self):
        
        for record in self:
            if record.type1_opcpta_id:
                record.code_base = record.type1_opcpta_id.type1_opcpta
            


class Compta_Paiement(models.Model):
    
    _name="compta_paiement_dep"
    _rec_name = "num_ch_emis"
    
    
    num_ch_emis= fields.Integer("N° Opération", readonly=True)
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    #banque = fields.Many2one("compta_comptebanque", "Intitulé du compte", required=True)
    intbanque = fields.Many2one("compta_comptebanque", "Intitulé compte", required=True)
    numcptbanq = fields.Char("N° compte", readonly=True)
    mnt_ordre_virement = fields.Float("Montant chèque", readonly=True)
    date_emis = fields.Date("Emis le",default=fields.Date.context_today, required=True)
    reference = fields.Char("Référence chèque", required=True)
    destinataire = fields.Char('Dest/Bénéf', required=True)
    motif = fields.Text("Motif",size=300)
    type_ecriture = fields.Many2one("compta_type_ecriture",default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'B')]))
    id_imput = fields.Char()
    var_cpte = fields.Char()
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),], 'Sens', default = 'C')
    type_journal = fields.Many2one("compta_type_journal",default=lambda self: self.env['compta_type_journal'].search([('type_journal','=', 'JB')]))
    detail_ov_ids = fields.One2many("compta_cheq_dep", "paiement_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Confirmé'),
        ('P', 'Provisoire'),
        ], string ="Etat", default ='draft', required=True)
    


    #fonction pour remplir les numeror de compte
    @api.onchange('intbanque')
    def remplir_compte(self):
        self.numcptbanq = self.intbanque.num_compte
        self.id_imput = self.intbanque.no_imputation.souscpte
        self.var_cpte = self.intbanque.no_imputation.souscpte.id
        

    @api.multi
    def action_draftc(self):
        self.write({'state': 'draft'})
        
    @api.multi
    def action_confirmerc(self):
         
        val_ex = int(self.x_exercice_id.id)
        val_struct = int(self.company_id.id)
        id_paie = self.id
        
        self.env.cr.execute("select numcheq + 1 from compta_compteur_cheq_emis where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        nu_cheq = self.env.cr.fetchone()
        numcheq_ = nu_cheq and nu_cheq[0]
        if numcheq_ == None:
            self.num_ch_emis = int(1)
            self.env.cr.execute("""INSERT INTO compta_compteur_cheq_emis(x_exercice_id,company_id,numcheq)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,self.num_ch_emis))    
        else:
            self.num_ch_emis = nu_cheq and nu_cheq[0]
            self.env.cr.execute("UPDATE compta_compteur_cheq_emis SET numcheq = %d  WHERE x_exercice_id = %d and company_id = %d" %(self.num_ch_emis,val_ex,val_struct))

        
        self.env.cr.execute("""SELECT sum(montant)
        FROM compta_cheq_dep WHERE x_exercice_id = %d AND company_id = %d AND paiement_id = %d """ %(val_ex, val_struct, id_paie))
        res = self.env.cr.fetchone()
        self.mnt_ordre_virement = res and res[0] or 0
        val_mnt = self.mnt_ordre_virement
        
        self.write({'state': 'C'})
        
        
    #Fonction compteur et génération des numéros des ecritures et des lignes d'ecritures
    @api.multi
    def generer_ecriture(self):
        
        self.write({'state': 'P'})
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_ecr = self.no_ecr
        id_paie = self.id
        var_cptes = int(self.var_cpte)
        vl_mnt = self.mnt_ordre_virement
        val_sens = str(self.fg_sens)
        val_date = self.date_emis
        v_type = self.type_ecriture

        #Attribution des numero et lignes d'ecritures pour l'enregistrement des cheques emis 
 
        self.env.cr.execute("""SELECT count(l.id) from compta_cheq_dep l where l.paiement_id = %d and l.company_id = %d and l.x_exercice_id = %d and l.retenue = True""" %(id_paie, val_struct, val_ex ))
        res = self.env.cr.fetchone()
        resu = res and res[0] or 0   

        if resu > 0:
            raise ValidationError(_("Il existe au moins une retenue. Veuillez la ou les traiter avant de poursuivre votre opération."))
        else:
            self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
            noecr = self.env.cr.dictfetchall()
            no_ecrs = noecr and noecr[0]['no_ecr']
            no_ecrs1 = noecr and noecr[0]['no_lecr']
            no_ecr = no_ecrs
           
            
            if not(no_ecr):           
                self.no_ecr = 1
                no_ecrs1 = 0
                for record in self.detail_ov_ids:
                    no_ecrs1 = no_ecrs1 + 1
                    record.no_lecr = no_ecrs1 
                self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
            else:
                self.no_ecr = no_ecr + 1
                no_ecrs11 = no_ecrs1 + 1
                no_ecrs1= no_ecrs11
                for record in self.detail_ov_ids:           
                    no_ecrs1 = no_ecrs1 + 1
                    record.no_lecr = no_ecrs1 
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
            
            for record in self.detail_ov_ids:
                val = (self.no_ecr)
                val_id = (self.id)
                self.env.cr.execute("UPDATE compta_cheq_dep SET no_ecr = %s WHERE paiement_id = %s", (val, val_id))
            
            self.env.cr.execute("select * from compta_paiement_dep where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_paie))
            curs_paiement = self.env.cr.dictfetchall()
            no_ecrs = curs_paiement and curs_paiement[0]['no_ecr']
            no_ecr = int(no_ecrs)
            typ_jr = curs_paiement and curs_paiement[0]['type_journal']
            typ_ecr = curs_paiement and curs_paiement[0]['type_ecriture']
            
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr,dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BE', %s, %s, 'P')" ,(no_ecr, val_date, typ_ecr, typ_jr, val_ex, val_struct))
    
            self.env.cr.execute("select * from compta_cheq_dep where x_exercice_id = %d and company_id = %d and paiement_id = %d " %(val_ex,val_struct, id_paie))
            curs_cheq_dep = self.env.cr.dictfetchall()
            
            var_ecr = self.no_ecr
            
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id,dt_ligne, fg_sens, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'P') """ ,(var_ecr,no_ecrs11, var_cptes, vl_mnt,val_ex, val_struct, val_date, val_sens))
               
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, ref_pj, mt_lecr, type_pj, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            SELECT no_ecr, no_lecr , id_imput, ref_pj, montant, type_pj, x_exercice_id, company_id, fg_sens, date_emis,fg_etat 
            FROM compta_cheq_dep WHERE x_exercice_id = %d AND company_id = %d AND paiement_id = %d """ %(val_ex, val_struct, id_paie))

        for vals in self.detail_ov_ids:
            val_mdt = vals.ref_pj
            if vals.type_pj.libelle.refe == '31':
                self.env.cr.execute("update budg_mandat set state = 'F' where x_exercice_id = %s and company_id = %s and no_mandat = %s" ,(val_ex, val_struct, val_mdt))
            elif vals.type_pj.libelle.refe == '30':
                self.env.cr.execute("update budg_op set et_doss = 'F' where x_exercice_id = %s and company_id = %s and no_op = %s" ,(val_ex, val_struct, val_mdt))
    
            vals.env.cr.execute("select count(id) from compta_retenue_cheq_emis where x_exercice_id = %d and company_id = %d and numcheq = %d" %(val_ex,val_struct, id_paie))
            re = self.env.cr.fetchone()
            resultat = re and re[0] or 0
            if resultat != 0:

                vals.env.cr.execute("""SELECT * from compta_retenue_cheq_emis l where l.numcheq = %d and l.company_id = %d and l.x_exercice_id = %d """ %(id_paie, val_struct, val_ex ))
                rows = vals.env.cr.dictfetchall()
                
                mnt = rows and rows[0]['mnt_retenue']
                typ_pj = rows and rows[0]['type_journal']
                typ_ecr = rows and rows[0]['type_ecriture']
                typ_op = rows and rows[0]['typ_op']
                pj = rows and rows[0]['ty_pj']
                ref = rows and rows[0]['ref_pj']
                an = rows and rows[0]['anne_pj']
                dt = rows and rows[0]['dte']
                var_cptes = rows and rows[0]['id_imput']
                code1 = rows and rows[0]['code1']
                code2 = rows and rows[0]['code2']
                
                self.env.cr.execute("select no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
                noecr = self.env.cr.dictfetchall()
                no_ecrs1 = noecr and noecr[0]['no_lecr']
                no_lecr1 = no_ecrs1 + 1
                
        
                v_lblecr = 'BO' + '-' + 'C' + '-' + str(code1) + '-' + str(code2) + '-' + str(self.x_exercice_id.no_ex) + '-' + str(ref)
                print('libelle', v_lblecr)
        
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture (no_ecr,no_lecr, no_souscptes, lb_lecr, type_pj, ref_pj, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens,fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'C', 'P') """, (no_ecr, no_lecr1, var_cptes, v_lblecr, pj, ref, mnt, val_ex, val_struct, dt))
                
                
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_lecr1,val_ex,val_struct))

                
                
    
class Compta_Detail_Ordre_Virement(models.Model):
    
    _name = "compta_cheq_dep"
    
    no_ecr = fields.Integer()
    no_lecr = fields.Integer("N° Lignes", readonly=True)
    paiement_id = fields.Many2one("compta_paiement_dep", ondelete = 'cascade')
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", domain = [('code', '=like', 'D%')], required=True)
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1), ('fg_ch_emis','=',True)]", required=True)
    code2 = fields.Char()
    code1 = fields.Char()
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération", required=False)
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Nature d'opération", required=False)
    type2_operation = fields.Many2one("compta_reg_op_banque_unique", "Type d'opération")
    nature_id = fields.Many2one("compta_table_listnat", 'Nature éventuelle')
    no_imputation = fields.Char()
    id_imput = fields.Integer()
    date_emis = fields.Date(default=fields.Date.context_today)
    type1_pj = fields.Selection([
        ('M', 'Mandat'),
        ('OP', 'Ordre de paiement')
        ], string = 'Pièce Just.')
    montant = fields.Float("Montant", readonly=True)
    type_pj = fields.Many2one('compta_piece_line', 'Pièce Just.', domain="[('type2','=',type2)]", required=True)
    annee_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="An. PJ")
    ref_pj = fields.Char("Ref. Pj", required=True)
    ref_pj0 = fields.Many2one("budg_op","Ref. OP",domain=[('et_doss', '=', 'V')])
    ref1_pj = fields.Many2one("budg_mandat","Ref. MDT",domain=[('state', '=', 'E')])
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),], 'Sens', default = 'D')
    fg_etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Vérifié'),
        ('R', 'Rejété')], 'Etat', default= 'P')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    retenue = fields.Boolean("Retenue ?")
    v_op = fields.Char()
    v_ope = fields.Char()
    
    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2 :
                val.code2 = val.type2.type_opcpta1
    
    @api.onchange('type1')
    def Cod1(self):
        for val in self:
            if val.type1 :
                val.code1 = val.type1.code
    
    @api.onchange('ref_pj')
    def MontantMandat(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_mdt = str(self.ref_pj)
        val_type = str(self.type_pj.libelle.refe)

        for val in self:

            if val_type == '30' and val.ref_pj:

                val.env.cr.execute("""select distinct mnt_op from budg_op where no_op = '%s' and
                               company_id = %d and x_exercice_id = %d""" %(val_mdt, val_struct, val_ex))
                ress = self.env.cr.fetchone()
                res2 = ress and ress[0] or 0

                self.montant = res2

            elif val_type == '31' and val.ref_pj:
        
                val.env.cr.execute("""select mnt_ord from budg_mandat where no_mandat = '%s' and
                company_id = %s and x_exercice_id = %s and state = 'E' """ %(val_mdt, val_struct, val_ex))
                res = self.env.cr.fetchone()
                res1 = res and res[0] or 0

                self.montant = res1

            else:
                print("Vous n'avez pas choisi")
    
    @api.onchange('type_operation')
    def v_op1(self):
        if self.type_operation:
            self.v_op = self.type_operation.type1_opcpta
    
    @api.onchange('type2_op')
    def v_op2(self):
        if self.type2_op:
            self.v_ope = self.type2_op.type2_opcpta.type_opcpta1
            
  
    
    @api.onchange('type2','type1')
    @api.model
    def get_imputationbq(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1.id)
        val_type2 = str(self.code2)
        #val_idtlv = int(self.id_tlv.id)
        #print('val id',val_idtlv)
        #val_type22 = str(self.type2_op.id.type2_op)
       
        #self.env.cr.execute("""select R.souscompte_id, R.fg_term from  compta_reg_op_guichet_unique R where R.type1_opcpta = %d and R.id = %d and R.x_exercice_id = %d and R.company_id = %d""" %(val_type1,val_type2, val_ex, val_struct))
        #Nouvelle requete
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from compta_type_op_cpta r where r.typebase_id = %s and type_opcpta1 = %s""" ,(val_type1,val_type2))
              #self.env.cr.execute("""select CD_NAT, LB_NAT, LV_NAT FROM "+" V_NM_TLV +" WHERE " + V_WH_TLV .concate_souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.no_imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        if val_type1 != False and val_type2 != False:
            
            #if terminal == 'T':
            self.id_imput = imput and imput[0]["souscompte_id"]
            """else:
                if val_type2 != False:                                       
                    self.env.cr.execute("select nm_listnat, clause_where from compta_table_listnat where id = 1 " )
                    res = self.env.cr.dictfetchall()
                    nom_vue = res and res[0]["nm_listnat"]
                    print('le nom vue',nom_vue)
                    clause_w = res and res[0]["clause_where"] 
                    print('la clause',clause_w)                  
                    #self.env.cr.execute("select cd_nat, lb_nat from %s where  %s" %(nom_vue,clause_w))
                    #nature = self.env.cr.dictfetchall()
                    #return [(x.cd_nat, x.lb_nat) for x in nature]
                    #print('valeur nature',nature)
            #return nature
                    #nature = self.env['compta_colonne_caisse'].search([])
                    #return [(x.cd_col_caise, x.lb_court) for x in nature]
                    #self.no_imputation = nature and nature[0]["vl_nat"]
                    #print('la val imputation',self.no_imputation)
                    #id_tlv = fields.Selection(selection = get_imputation, string= 'Nature éventuelle')
            """
    
    

class Compta_Compteur_cheq_emis(models.Model):
    
    _name = "compta_compteur_cheq_emis"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    numcheq = fields.Integer(default = 0)

class Compta_Compteur_cheq_rec(models.Model):
    
    _name = "compta_compteur_cheq_rec"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    numcheqrec = fields.Integer(default = 0)



class Compta_retenue(models.Model):
    _name='compta_retenue'
    _rec_name = "numord"
    

    fg_etat = fields.Char('Etat')
    numord = fields.Many2one( "compta_paiement_ordre","N° Opération", required=True, domain = [('state', '=', 'C')])
    destinataire = fields.Char("Destinataire", readonly=True)
    benef = fields.Char("Bénéficiaire", readonly=True)
    mnt_op = fields.Integer("Montant opération", readonly=True )
    mnt_retenue = fields.Integer('Montant retenu', required=True)
    typ_op = fields.Char('Type Opération')
    id_op = fields.Integer()
    dte = fields.Date(default=fields.Date.context_today)
    ty_pj = fields.Many2one('compta_piece_line', 'Type PJ', domain="[('type2','=',type2)]", required=False)
    ref_pj = fields.Char('Ref PJ', required=False)
    anne_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Année", required=True)
    nm_benef = fields.Char("Nom bénéficiaire", required=False)
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", required=True, domain = [('code', '=like', 'E%')])
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1), ('fg_retenue','=',True)]", required=True)
    code1 = fields.Char()
    code2 = fields.Char()
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération", required=False)
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Nature d'opération", required=False)
    id_tlv = fields.Many2one("compta_table_listnat", string = 'Nature détaillée')
    cd_nat = fields.Char()
    id_imput = fields.Integer()
    var_cpte = fields.Integer()
    type_ecriture = fields.Many2one("compta_type_ecriture",default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=','R')]))
    type_journal = fields.Many2one("compta_type_journal",default=lambda self: self.env['compta_type_journal'].search([('type_journal','=','JO')]))
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('N','Nouveau'),
        ('V', 'Validé'),
        ], default="N")
            
    @api.onchange('numord')
    def onchangenumord(self):
        
        if self.numord:
            self.destinataire = self.numord.destinataire
            self.mnt_op = self.numord.mnt_ordre_virement
    
    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2 :
                val.code2 = val.type2.type_opcpta1
                
    @api.onchange('type1')
    def Cod1(self):
        for val in self:
            if val.type1 :
                val.code1 = val.type1.code
                
    @api.onchange('type2','type1')
    @api.model
    def get_imputation_ordre(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1.id)
        val_type2 = str(self.code2)
        
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from compta_type_op_cpta r where r.typebase_id = %s and type_opcpta1 = %s""" ,(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        if val_type1 != False and val_type2 != False:
            
            if terminal == 'T':  
                self.id_imput = imput and imput[0]["souscompte_id"]
        
    
    def valider_retenue(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.numord)
        
        mnt = int(self.mnt_retenue)
        
        self.env.cr.execute("UPDATE compta_paiement_ordre SET mnt_ordre_virement = mnt_ordre_virement - %d WHERE id = %d and x_exercice_id = %d and company_id = %d" %(mnt, v_id, val_ex, val_struct))
        self.write({'state': 'V'})
      
        
        #mnt = self.mnt_retenue
        #typ_pj = int(self.type_journal)
        #typ_ecr = int(self.type_ecriture)
        #typ_op = self.typ_op
        #pj = int(self.ty_pj)
        #ref = self.ref_pj
        #an = int(self.anne_pj)
        #dt = self.dte
        #var_cptes = self.id_imput
        
        #self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        #noecr = self.env.cr.dictfetchall()
        #no_ecrs = noecr and noecr[0]['no_ecr']
        #no_ecrs1 = noecr and noecr[0]['no_lecr']
        #no_ecr = no_ecrs + 1
        #no_lecr = no_ecrs1 + 1
        
        #self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BE', %s, %s, 'P')" ,(no_ecr, dt, typ_ecr, typ_pj, val_ex, val_struct))

        #v_lblecr = 'BO' + '-' + 'C' + '-' + str(self.code1) + '-' + str(self.code2) + '-' + str(self.x_exercice_id.no_ex) + '-' + str(ref)
        #print('libelle', v_lblecr)

        #self.env.cr.execute("""INSERT INTO compta_ligne_ecriture (no_ecr,no_lecr, no_souscptes, lb_lecr type_pj, ref_pj, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens,fg_etat) 
        #VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'C', 'P') """ , (no_ecr, no_lecr, var_cptes, v_lblecr, pj, ref, mnt, val_ex, val_struct, dt))
        
        #v_lecr = no_lecr + 1

        #self.env.cr.execute("""INSERT INTO compta_ligne_ecriture (no_ecr,no_lecr, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens,fg_etat) 
        #VALUES (%s, %s, %s, %s, %s, %s, 'D', 'P') """ , (no_ecr, no_lecr, mnt, val_ex, val_struct, dt))
                
        #self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecr,v_lecr,val_ex,val_struct))

        self.env.cr.execute("""UPDATE compta_paiement_ordre_line SET retenue = False WHERE retenue = True and
        x_exercice_id = %d and company_id = %d and paiement__ordre_id = %d """ %(val_struct, val_ex, v_id))


class Compta_retenue_cheq(models.Model):
    _name='compta_retenue_cheq_emis'
    _rec_name = "numcheq"
    

    fg_etat = fields.Char('Etat')
    numcheq = fields.Many2one( "compta_paiement_dep","N° Opération", required=True, domain = [('state', '=', 'C')])
    destinataire = fields.Char("Destinataire", readonly=True)
    benef = fields.Char("Bénéficiaire", readonly=True)
    mnt_op = fields.Integer("Montant opération", readonly=True )
    mnt_retenue = fields.Integer('Montant retenu', required=True)
    typ_op = fields.Char('Type Opération', default="BE")
    type_ecriture = fields.Many2one("compta_type_ecriture",default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=','R')]))
    id_op = fields.Integer()
    dte = fields.Date(default=fields.Date.context_today)
    type_journal = fields.Many2one("compta_type_journal",default=lambda self: self.env['compta_type_journal'].search([('type_journal','=','JO')]))
    ty_pj = fields.Many2one('compta_piece_line', 'Type PJ', domain="[('type2','=',type2)]", required=False)
    ref_pj = fields.Char('Ref PJ', required=False)
    anne_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Année", required=True)
    nm_benef = fields.Char("Nom bénéficiaire", required=False)
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", required=True, domain = [('code', '=like', 'D%')])
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1), ('fg_retenue','=',True)]", required=True)
    code1 = fields.Char()
    code2 = fields.Char()
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération", required=False)
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Nature d'opération", required=False)
    id_tlv = fields.Many2one("compta_table_listnat", string = 'Nature détaillée')
    cd_nat = fields.Char()
    id_imput = fields.Integer()
    var_cpte = fields.Integer()
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('N','Nouveau'),
        ('V', 'Validé'),
        ], default="N")
    
    @api.onchange('numcheq')
    def onchangenumcheq(self):
        
        if self.numcheq:
            self.destinataire = self.numcheq.destinataire
            self.mnt_op = self.numcheq.mnt_ordre_virement
            
    
    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2 :
                val.code2 = val.type2.type_opcpta1
                
    @api.onchange('type1')
    def Cod1(self):
        for val in self:
            if val.type1 :
                val.code1 = val.type1.code
                
    @api.onchange('type2','type1')
    @api.model
    def get_imputation_ordre(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1.id)
        val_type2 = str(self.code2)
        
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from compta_type_op_cpta r where r.typebase_id = %s and type_opcpta1 = %s""" ,(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        if val_type1 != False and val_type2 != False:
            
            if terminal == 'T':  
                self.id_imput = imput and imput[0]["souscompte_id"]
        
    
    def valider_retenue(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.numcheq)
        
        mnt = int(self.mnt_retenue)
        
        self.env.cr.execute("UPDATE compta_paiement_dep SET mnt_ordre_virement = mnt_ordre_virement - %d WHERE id = %d and x_exercice_id = %d and company_id = %d" %(mnt, v_id, val_ex, val_struct))
        self.write({'state': 'V'})
        
        #mnt = self.mnt_retenue
        #typ_pj = int(self.type_journal)
        #typ_ecr = int(self.type_ecriture)
        #typ_op = self.typ_op
        #pj = int(self.ty_pj)
        #ref = self.ref_pj
        #an = int(self.anne_pj)
        #dt = self.dte
        #var_cptes = int(self.id_imput)
        
        #self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        #noecr = self.env.cr.dictfetchall()
        #no_ecrs = noecr and noecr[0]['no_ecr']
        #no_ecrs1 = noecr and noecr[0]['no_lecr']
        #no_ecr = no_ecrs + 1
        #no_lecr = no_ecrs1 + 1
        
        #self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BE', %s, %s, 'P')" ,(no_ecr, dt, typ_ecr, typ_pj, val_ex, val_struct))

        #v_lblecr = 'BO' + '-' + 'C' + '-' + str(self.code1) + '-' + str(self.code2) + '-' + str(self.x_exercice_id.no_ex) + '-' + str(ref)
        #print('libelle', v_lblecr)

        #self.env.cr.execute("INSERT INTO compta_ligne_ecriture (no_ecr,no_lecr, no_souscptes, lb_lecr, type_pj, ref_pj, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens,fg_etat) 
        #VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'C', 'P') ", (no_ecr, no_lecr, var_cptes, v_lblecr, pj, ref, mnt, val_ex, val_struct, dt))
        
        #v_lecr = no_lecr + 1
        
        #self.env.cr.execute("INSERT INTO compta_ligne_ecriture (no_ecr,no_lecr, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens,fg_etat) 
        #VALUES (%s, %s, %s, %s, %s, %s, 'D', 'P') " , (no_ecr, v_lecr, mnt, val_ex, val_struct, dt))
       
        
        #self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecr,v_lecr,val_ex,val_struct))

        self.env.cr.execute("""UPDATE compta_cheq_dep SET retenue = False WHERE retenue = True and
        x_exercice_id = %d and company_id = %d and paiement_id = %d""" %(val_struct, val_ex, v_id))


class Compta_ModReg(models.Model):
    
    _name = 'compta_regmodreg'
    
    modreg_id = fields.Many2one("ref_modereglement", 'Mode de règlement', required=True)
    cpte_reg = fields.Many2one("compta_plan_line", 'Compte de règlement', required=True)
    
 #classe pour pour le choix du mode de reglement d'un mandat   
class ModeReglementMandat(models.Model):
    
    _name = "compta_moderegmandat"
    _rec_name = 'mode_reg_id'
    
    mode_reg_id = fields.Many2one("ref_modereglement", 'Mode de règlement', required=True)
    no_mandat = fields.Many2one("budg_mandat", 'Référence mandat',domain=[('state', '=', 'I')], required=True)
    cd_titre_id = fields.Char(string="Titre", readonly=True)
    cd_section_id = fields.Char(string="Section", readonly=True)
    cd_chapitre_id = fields.Char(string="Chapitre", readonly=True)
    cd_article_id = fields.Char(string="Article", readonly=True)
    cd_paragraphe_id = fields.Char(string="Paragraphe", readonly=True)
    cd_rubrique_id = fields.Char(string="Rubrique", readonly=True)
    no_lo = fields.Char("N° Liquidation", readonly=True)
    no_eng = fields.Char("N° engagement", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    date_mandat = fields.Date("Date")
    objet = fields.Text('Objet', readonly=True)
    banque = fields.Many2one("res.bank", 'Banque')
    numcompte = fields.Char('N° Compte')
    state = fields.Selection([
        ('N', 'Nouveau'),
        ('C', 'Confirmé'),
        ], string ="Etat", default ='N')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    @api.multi
    def action_modreg_confirme(self):
        
        val_mandat = str(self.no_mandat.no_mandat)
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        var_mode = int(self.mode_reg_id)
        
        self.env.cr.execute("UPDATE budg_mandat SET modereg = %s WHERE no_mandat = %s and x_exercice_id = %s and company_id = %s" ,(var_mode, val_mandat, val_ex, val_struct))
       
        self.write({'state': 'C'})


    #Chargement du mandat choisi
    @api.onchange('no_mandat')
    def no_lo_on_change(self):

        if self.no_mandat:
            
            self.date_mandat = self.no_mandat.dt_etat
            self.objet = self.no_mandat.obj
            self.montant = self.no_mandat.mnt_eng
            self.no_eng = self.no_mandat.no_eng
            self.no_lo = self.no_mandat.no_lo.no_lo
            self.cd_titre_id = self.no_mandat.cd_titre_id
            self.cd_section_id = self.no_mandat.cd_section_id
            self.cd_chapitre_id = self.no_mandat.cd_chapitre_id
            self.cd_article_id = self.no_mandat.cd_article_id
            self.cd_paragraphe_id = self.no_mandat.cd_paragraphe_id
            self.cd_rubrique_id = self.no_mandat.cd_rubrique_id
            
#classe pour pour le choix du mode de reglement d'un titre de recette   
class ModeReglementTitre(models.Model):
    
    _name = "compta_moderegtitre"
    _rec_name = 'moderec_id'
    
    moderec_id = fields.Many2one("ref_modereglement", 'Mode de recouvrement', required= True)
    notitre = fields.Many2one("budg_titrerecette", 'Référence titre de recette',domain=[('et_doss', '=', 'E')], required=True)
    cd_titre_id = fields.Char(string="Titre", readonly=True)
    cd_section_id = fields.Char(string="Section", readonly=True)
    cd_chapitre_id = fields.Char(string="Chapitre", readonly=True)
    cd_article_id = fields.Char(string="Article", readonly=True)
    cd_paragraphe_id = fields.Char(string="Paragraphe", readonly=True)
    cd_rubrique_id = fields.Char(string="Rubrique", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    date_titre = fields.Date("Date", readonly=True)
    objet = fields.Text('Objet', size=300, readonly=True)
    banque = fields.Many2one("res.bank", 'Banque')
    numcompte = fields.Char('N° Compte',size=20)
    state = fields.Selection([
        ('N', 'Nouveau'),
        ('C', 'Confirmé'),
        ], string ="Etat", default ='N')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
  
    @api.multi
    def action_modrec_confirme(self):
        
        val_titre = str(self.notitre.cd_titre_recette)
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        var_mode = int(self.moderec_id)
        
        self.env.cr.execute("UPDATE budg_titrerecette SET cd_mode_mp_id = %s WHERE cd_titre_recette = %s and x_exercice_id = %s and company_id = %s" ,(var_mode, val_titre, val_ex, val_struct))
        
        self.write({'state': 'C'})
    
    #Chargement du titre de recette choisi
    @api.onchange('notitre')
    def onchangenotitre(self):

        if self.notitre:
            
            self.objet = self.notitre.lb_objet
            self.montant = self.notitre.mnt_rec
            self.date_titre = self.notitre.dt_rec
            self.cd_titre_id = self.notitre.cd_titre_id.titre.titre
            self.cd_section_id = self.notitre.cd_section_id.section.section
            self.cd_chapitre_id = self.notitre.cd_chapitre_id.chapitre.chapitre
            self.cd_article_id = self.notitre.cd_article_id.article.article
            self.cd_paragraphe_id = self.notitre.cd_paragraphe_id.paragraphe.paragraphe
            self.cd_rubrique_id = self.notitre.cd_rubrique_id.concate_rubrique



class Compta_RegleCompteTiers(models.Model):
    
    _name = 'compta_reglecomptetiers'

    titre_id = fields.Many2one('budg_titre', string = 'Titre')
    type_beneficiaire = fields.Many2one('budg_typebeneficiaire', string = 'Type benef')
    mode_reglement = fields.Many2one('ref_modereglement', string = 'Mode de règlement')
    no_imputation = fields.Many2one('ref_souscompte', string = 'Imputation comptable')

#Classe inutilisée pour le moment
class Reg_OP_Guichet(models.Model):
    _name='compta_reg_op_guichet'
    _rec_name = 'type1_opcpta_id'
    
    type1_opcpta_id = fields.Many2one("compta_type_op_cpta_line", 'Libellé de type de base')
    type_opguichet_ids = fields.One2many('compta_type_op_cpta','reg_op_guichet')




#Nouvelle classe regle operation de guichet saisie unique
class Reg_Op_Guichet_Unique(models.Model):
    _name = 'compta_reg_op_guichet_unique'
    _rec_name = "type2_opcpta"
    
    type1_opcpta = fields.Many2one("compta_type1_op_cpta", 'Libellé de type de base', required=True)
    type2_opcpta = fields.Many2one("compta_type_op_cpta", string="Type opération guichet", required=True)
    no_imputation = fields.Many2one("ref_souscompte", 'Imputation old')
    fg_term = fields.Selection([
        ('T', 'Y-Terminal'),
        ('N', 'N-Non (ici)'),
        ('L', 'L-Non(Lv)'),
        ], 'Niveau de determination', default='T', index=True, required=True, copy=False, track_visibility='always')
    imputation = fields.Many2one('ref_souscompte', 'old Imputation')
    
    #Me rappeler enlever le S
    imputation = fields.Many2one('compta_plan_line', 'Imputation')
    souscompte_id = fields.Integer()
    list_val = fields.Many2one("compta_table_listnat", 'Elément liste')
    #Ajouter ces deux champs
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
  
    
    @api.onchange('imputation')
    def OnchangeImputation(self):
        if self.imputation:
            self.souscompte_id = self.imputation.souscpte.id
    
#classe mere d'enregistrement d'une opération de guichet libre

class compta_op_guichet(models.Model):
    
    _name = 'compta_op_guichet'
    _rec_name = 'no_op'
    
    no_op = fields.Integer("N° Op. Guichet", readonly=True)
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    type_operation = fields.Many2one("compta_data", string="Type Op. Guichet", required = True)
    mode_reglement = fields.Many2one("compta_jr_modreg", 'Mode de règlement', required = True)
    date_ope = fields.Date("Date",default=fields.Date.context_today)
    type_journal = fields.Char("Journal", readonly=True)
    type_op = fields.Char(default = 'G')
    var_jr = fields.Integer()
    var_cpte = fields.Integer()
    mnt_total = fields.Integer()
    compte = fields.Char('Compte')
    test1 = fields.Char()
    type_intervenant = fields.Many2one("compta_type_interv_ext", 'Type intervenant')
    nom_intervenant = fields.Char('Nom intervenant', size = 35)
    fg_sens = fields.Char(size=1)
    compta_quittance = fields.Many2one("compta_quittance", "quittance")
    no_jour = fields.Integer("N° jour")
    dte = fields.Date(default=fields.Date.context_today)
    ope_comptable_ids = fields.One2many("compta_op_cpta", 'id_op_guichet_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Confirmé'),
        ('P', 'Provisoire'),
        ], string ="Etat", default ='draft', required=True)
    
    
    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
    
    @api.multi
    def action_confirmer(self):
        self.write({'state': 'C'})
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select numop from compta_compteur_op_guichet where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        nu_op = self.env.cr.fetchone()
        numop = nu_op and nu_op[0] or 0
        c1 = int(numop) + 1
        c = str(numop)
        if c == "0":
            ok = str(c1).zfill(4)
            self.no_op = ok
            vals = c1
            self.env.cr.execute("""INSERT INTO compta_compteur_op_guichet(x_exercice_id,company_id,numop)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,self.no_op))    
        else:
            c1 = int(numop) + 1
            c = str(numop)
            ok = str(c1).zfill(4)
            self.no_op = ok
            vals = c1
            self.env.cr.execute("UPDATE compta_compteur_op_guichet SET numop = %d  WHERE x_exercice_id = %d and company_id = %d" %(self.no_op,val_ex,val_struct))


    def function_test(self):
        #clause_w = str('cd_nat = 2')
        
        #nature = self.env['test'].search([])
        #return [(x.cd_nat, x.lb_nat) for x in nature]
        
        vue = str('test')
        print('voici vue', vue)
        self.env.cr.execute("""select * from %s """ %(vue))
        #nature = self.env['test'].search([])
        for line in self.env.cr.dictfetchall():
            
            #nature = self.env.cr.dictfetchall()
            v_id = line['id']
            v_libelle = line['lb_long']
            #return [(v_id, v_libelle)]
            #self.test1 = v_id
            self.test1 = v_libelle

    
    @api.onchange('type_operation')
    def filtre(self):
        if self.type_operation.cd_data == 'E':
            self.env.cr.execute("select type1_opcpta from compta_type1_op_cpta where type1_opcpta like 'E%'")
            type1 = self.env.cr.dictfetchall()
            self.ope_comptable_ids.type1_opcpta = type1 and type1[0]['type1_opcpta']
    
#fonction pour remplir le champ journal
    @api.onchange('mode_reglement')
    def remplir_champ(self):
        self.type_journal = self.mode_reglement.journal_id.lb_long
        self.compte = self.mode_reglement.no_imputation.souscpte.id
        
        self.var_jr = self.mode_reglement.journal_id.id  
        self.var_cpte = self.mode_reglement.no_imputation.souscpte.id
     
     
    @api.onchange('type_operation')
    def type_sens(self):
        if self.type_operation.cd_data == 'E':
            self.fg_sens = 'C'
        else:
            self.fg_sens = 'D'
              
              
    @api.multi
    def generer_ecriture_guichet(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        id_guichet = self.id
        var_jrs = int(self.var_jr)
        var_cptes = int(self.var_cpte)
        val_date = str(self.dte)
        
        self.write({'state': 'P'})
        
        self.env.cr.execute("""SELECT sum(mnt_op_cpta)
        FROM compta_op_cpta WHERE x_exercice_id = %d AND company_id = %d AND id_op_guichet_id = %d """ %(val_ex, val_struct, id_guichet))
        res = self.env.cr.fetchone()
        self.mnt_total = res and res[0]
        val_mnt = self.mnt_total
        
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
       
       
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.ope_comptable_ids:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            no_ecrs11 = no_ecrs1 + 1
            no_ecrs1= no_ecrs11
            for record in self.ope_comptable_ids:           
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
        
        for record in self.ope_comptable_ids:
            val = (self.no_ecr)
            val_id = (self.id)
            self.env.cr.execute("UPDATE compta_op_cpta SET no_ecr = %s WHERE id_op_guichet_id = %s" ,(val, val_id))

        self.env.cr.execute("select * from compta_op_guichet where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_guichet))
        curs_op_guichet = self.env.cr.dictfetchall()
        no_ecrs = curs_op_guichet and curs_op_guichet[0]['no_ecr']
        no_ecr = int(no_ecrs)
        fg_sens11 = curs_op_guichet and curs_op_guichet[0]['fg_sens']
        fg_sens1 = str(fg_sens11)
        typ_op = curs_op_guichet and curs_op_guichet[0]['type_op']
        ty_op = str(typ_op)

        self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr dt_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, 'G', %s, %s, 'P')" ,(no_ecr, val_date, var_jrs, val_ex, val_struct))
        
        self.env.cr.execute("select * from compta_op_cpta where x_exercice_id = %d and company_id = %d and id_op_guichet_id = %d " %(val_ex,val_struct, id_guichet))
        curs_op_cpta = self.env.cr.dictfetchall()
        
        var_ecr = self.no_ecr
        
        self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'P') """ ,(var_ecr,no_ecrs11, var_cptes, val_mnt,val_ex, val_struct, fg_sens1, val_date))
           
        self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, fg_sens, type_pj, x_exercice_id, company_id, dt_ligne,fg_etat) 
        SELECT no_ecr, no_lecr , id_imput, mnt_op_cpta, fg_sens, typ_pj, x_exercice_id, company_id, dte_op, fg_etat
        FROM compta_op_cpta WHERE x_exercice_id = %s AND company_id = %s AND id_op_guichet_id = %s """ ,(val_ex, val_struct, id_guichet))

        @api.multi
        def Quittance(self):
            return {
                
                'res_model': 'compta_quittance',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref("compta_quittance.view_quittance_form").id,
                'target': new
                }

#classe fille d'enregistrement d'une opération de guichet libre

class compta_op_cpta(models.Model):
    
    _name = 'compta_op_cpta'
    
    no_ecr =fields.Integer()
    no_lecr = fields.Integer("N° Ligne", readonly=True)
    id_op_guichet_id = fields.Many2one("compta_op_guichet",ondelete='cascade')
    typ_pj = fields.Many2one("compta_piece", string='Pièce Just.', required=True)
    an_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Année")
    ref_pj = fields.Char("Ref. PJ", required=True)
    mnt_op_cpta = fields.Integer("Montant", required=True)
    type1_op_cpta = fields.Many2one("compta_type1_op_cpta","Catégorie d'opération", required=True)
    type2_op_cpta = fields.Many2one("compta_reg_op_guichet_unique","Nature opération", required=True)
    cd_nats = fields.Many2one('testok', string = 'Nature détaillée')
    #id_tlv = fields.Many2one("compta_table_listnat", string = 'Nature détaillée')
    id_tlv = fields.Char()
    no_imput = fields.Many2one("ref_souscompte", 'Imputation')
    id_imput = fields.Integer()
    no_imputation = fields.Char('Imputation')
    fg_etat = fields.Selection([
        ('P', 'Annulé'),
        ('V', 'Vérifié'),
        ('R', 'Rejété')], 'Etat', default='P')
    fg_sens = fields.Char('Sens')
    dte_op = fields.Date(default=fields.Date.context_today)
    no_jour = fields.Integer("N° jour")
    mode_regelement = fields.Many2one("ref_modereglement", 'Mode de reglement')
    id_tlv_extra = fields.Many2one("compta_table_listnat", 'Nature')
    cd_nat_extra = fields.Char()
    fg_retenue = fields.Boolean("Retenue")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    @api.model
    def _function_test(self):
        #clause_w = str('cd_nat = 2')
        
        #nature = self.env['test'].search([])
        #return [(x.cd_nat, x.lb_nat) for x in nature]
        
        vue = str('test')
        self.env.cr.execute("""select id, lb_long from %s """ %(vue))
        #nature = self.env['test'].search([])
        nature = self.env.cr.dictfetchall()
        for vals in nature:
            return [(x.id, x.lb_long) for x in vals]
        #print('valeur test',nature)
    
    @api.onchange('type2_op_cpta','type1_op_cpta')
    @api.model
    def get_imputation(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1_op_cpta.id)
        val_type2 = int(self.type2_op_cpta.id)
       
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from  compta_reg_op_guichet_unique r where r.type1_opcpta = %d and r.id = %d and r.x_exercice_id = %d and r.company_id = %d""" %(val_type1,val_type2, val_ex, val_struct))
        #self.env.cr.execute("""select C.id, C.souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        #self.env.cr.execute("""select CD_NAT, LB_NAT, LV_NAT FROM "+" V_NM_TLV +" WHERE " + V_WH_TLV .concate_souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.no_imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        print("la valeur de temrinal", terminal)
        if val_type1 != False and val_type2 != False:
            
            if terminal == 'T':  
                #self.id_imput = imput and imput[0]["id"]
                self.id_imput = imput and imput[0]["souscompte_id"]
                #self.no_imputation = imput and imput[0]["souscpte"]
            else:
                if val_type2 != False:                                       
                    self.env.cr.execute("""select nm_listnat, clause_where from compta_table_listnat where id = 1 """ )
                    res = self.env.cr.dictfetchall()
                    nom_vue = res and res[0]["nm_listnat"]
                    print('le nom vue',nom_vue)
                    clause_w = res and res[0]["clause_where"] 
                    print('la clause',clause_w)                  
                    #self.env.cr.execute("select cd_nat, lb_nat from %s where  %s" %(nom_vue,clause_w))
                    #nature = self.env.cr.dictfetchall()
                    #return [(x.cd_nat, x.lb_nat) for x in nature]
                    #print('valeur nature',nature)
            #return nature
                    #nature = self.env['compta_colonne_caisse'].search([])
                    #return [(x.cd_col_caise, x.lb_court) for x in nature]
                    #self.no_imputation = nature and nature[0]["vl_nat"]
                    #print('la val imputation',self.no_imputation)
    #id_tlv = fields.Selection(selection = get_imputation, string= 'Nature éventuelle')
    
    
    @api.onchange('type1_op_cpta')
    def test(self):
            
        if self.id_op_guichet_id.type_operation.cd_data == 'E':
            self.fg_sens = 'D'
        else:
            self.fg_sens = 'C'
    
    
class Compta_quittance(models.Model):
    
    _name = 'compta_quittance'
    _rec_name = 'no_quittance'
    
    id_op_guichet = fields.Many2one("compta_op_guichet", string="N° opération")
    no_quittance = fields.Char("N° quittance", readonly=True)
    type_quittance_id = fields.Many2one("compta_type_quittance")
    nom_intervenant = fields.Char("Intervenant", readonly=True)
    tel_benef = fields.Char("Téléphone")
    type_ecriture = fields.Char("Téléphone")
    mode_reg = fields.Many2one("ref_modereglement", "Mode de règlement")
    mnt_op_gui = fields.Integer("Montant total")
    mnt_recu = fields.Integer("Montant reçu")
    mnt_rest = fields.Integer("Montant à restituer", compute='_mnt_restant')
    state = fields.Selection([
        ('V', 'Validé'),
        ('A', 'Annulé')], 'Etat')
    objet = fields.Text("Objet")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
   
    
    @api.onchange('id_op_guichet')
    def id_op_guichet_on_change(self):

        if self.id_op_guichet:
            self.mnt_op_gui = self.id_op_guichet.mnt_total
            self.nom_intervenant = self.id_op_guichet.nom_intervenant
            #self.objet = self.id_op_guichet.type2_op_cpta  
    
    
    @api.depends('mnt_op_gui','mnt_recu')
    def _mnt_restant(self):
        for x in self:
            x.mnt_rest = x.mnt_recu - x.mnt_op_gui         



    @api.multi
    def action_valider(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select noquittance from compta_compteur_quittance where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        quittance = self.env.cr.fetchone()
        no_quittance = quittance and quittance[0] or 0
        c1 = int(no_quittance) + 1
        c = str(no_quittance)
        if c == "0":
            ok = str(c1).zfill(4)
            self.no_quittance = ok
            vals = c1
            self.no_quittance = int(1)
            self.env.cr.execute("""INSERT INTO compta_compteur_quittance(x_exercice_id,company_id,noquittance)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))    
        else:
            self.no_quittance = quittance and quittance[0]
            c1 = int(no_quittance) + 1
            c = str(no_quittance)
            ok = str(c1).zfill(4)
            self.no_quittance = ok
            vals = c1
            self.env.cr.execute("UPDATE compta_compteur_quittance SET noquittance = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))

        self.write({'state': 'V'})
    
    @api.multi
    def action_annuler(self):
        self.write({'state': 'A'})

class Compta_compteur_quittance(models.Model):
    
    _name = "compta_compteur_quittance"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    noquittance = fields.Integer()



class compta_table_listnat(models.Model):
    
    _name = "compta_table_listnat"
    _rec_name = "lb_nature"
    
    nm_listnat = fields.Char("Code")
    clause_where = fields.Char("clause")
    lb_nature = fields.Char("Intitulé", required=True)
    ty_nature = fields.Many2one("compta_type_op_cpta", "Nature opération", required=True)
    

class DeuxCmpte(models.Model):
    _name = "compta_data"
    _rec_name = "type_operation"
    
    cd_data = fields.Char('Code data')
    type_operation = fields.Char("Libellé long")


#Class de parametrage journal-mode de reglement
class Journal_ModReg(models.Model):
    _name = 'compta_jr_modreg'
    name = fields.Many2one("ref_modereglement", 'Mode de règlement', required = True)
    type_quittance = fields.Many2one("compta_type_quittance", 'Type de quittance', required = False)
    no_imputation = fields.Many2one("compta_plan_line", 'Compte de règlement', required = True)
    souscpte = fields.Integer("Sous compte")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange("no_imputation")
    def ValCpte(self):
        for val in self:
            if self.no_imputation:
                self.souscpte = self.no_imputation.souscpte.id


class Reg_OP_Banque(models.Model):
    _name='compta_reg_op_banque'
    
    type1_opcpta_id = fields.Many2one("compta_type_op_banque_line", 'Libellé de type de base')
    type_opbanque_ids = fields.One2many('compta_type_op_banque','reg_op_banque')

  #fonction pour emplir les éléments de compta_type_op_banque
    @api.onchange('type1_opcpta_id')
    def remplir_champ(self):
        self.type_opbanque_ids = self.type1_opcpta_id.type_opbq_ids  
          
    
class Compta_CompteBanque(models.Model): 

    _name = "compta_comptebanque"
    _rec_name = "lb_long"
    
    x_banque_id = fields.Many2one('res.bank', string = "Banque", required = True)
    x_agence_id = fields.Many2one('ref_banque_agence',string="Agence", required=True)
    num_compte = fields.Char(string = "Numéro compte", required = True)
    lb_long = fields.Char("Intitulé du compte", required = True)
    no_imputation = fields.Many2one("compta_plan_line", "Imputation", required = True)
    active = fields.Boolean('Actif',default=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
   
    
class Compta_compteur_ecr(models.Model):
    
    _name = "compta_compteur_op_guichet"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    numop = fields.Integer(default = 0)


class Compta_compteur_avis(models.Model):
    
    _name = "compta_compteur_op_avis"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    numavis = fields.Integer(default = 0)
    

class Compta_piece(models.Model):
    _name = 'compta_piece'
    _rec_name = "pj_id"
    
    type_op = fields.Many2one("compta_reg_op_guichet_unique", required=True,string ="Type d'opération")
    pj_id = fields.Many2one("ref_piece_justificatives", required=True, string="Libellé pièce")
    

#classe pour faire un many2one de piece justificative
class Compta_PJ(models.Model):
    _name = 'compta_pj'
    _rec_name = "pj_id"
    
    pj_id = fields.Many2one("ref_piece_justificatives", string="Libellé pièce")
    compta_reg_op_guichet_unique_id = fields.Many2one("compta_reg_op_guichet_unique")


#creation des tables d'enregistrement ordre de virement
class ComptaOrdrePaiement(models.Model): 
    _name="compta_paiement_ordre"
    _rec_name = "num_ch_emis"
    
    
    num_ch_emis= fields.Integer("N° Opération", readonly=True)
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    intbanque = fields.Many2one("compta_comptebanque", "Intitulé compte", required=True)
    numcptbanq = fields.Char("N° compte", readonly=True)
    mnt_ordre_virement = fields.Integer("Montant virement",readonly = True)
    date_emis = fields.Date("Emis le",default=fields.Date.context_today,required=True)
    reference = fields.Char("Référence virement", required=True)
    destinataire = fields.Many2one('res.bank', string = 'Destinataire', required=True)
    id_imput = fields.Char()
    var_cpte = fields.Integer()
    type_journal = fields.Many2one("compta_type_journal",default=lambda self: self.env['compta_type_journal'].search([('type_journal','=', 'JB')]))
    type_ecriture = fields.Many2one("compta_type_ecriture",default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'B')]))
    motif = fields.Text("Motif",size=300)
    x_line_ids = fields.One2many("compta_paiement_ordre_line", "paiement__ordre_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Confirmé'),
        ('P', 'Provisoire'),
        ], string ="Etat", default ='draft', required=True)
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),], 'Sens', default = 'C')
    
    #fonction pour remplir le numero de compte
    @api.onchange('intbanque')
    def remplir_compte(self):
        self.numcptbanq = self.intbanque.num_compte
        self.id_imput = self.intbanque.no_imputation.souscpte.id
        self.var_cpte = self.intbanque.no_imputation.souscpte.id


    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        
    @api.multi
    def action_confirmer(self):
        self.write({'state': 'C'})
         
        val_ex = int(self.x_exercice_id.id)
        val_struct = int(self.company_id.id)
        id_ordre = self.id
        
        self.env.cr.execute("select numcheqrec + 1 from compta_compteur_cheq_rec where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        nu_cheq = self.env.cr.fetchone()
        numcheq_ = nu_cheq and nu_cheq[0]
        if numcheq_ == None:
            self.num_ch_emis = int(1)
            self.env.cr.execute("INSERT INTO compta_compteur_cheq_rec(x_exercice_id,company_id,numcheqrec)  VALUES(%d, %d, %d)" %(val_ex,val_struct,self.num_ch_emis))    
        else:
            self.num_ch_emis = nu_cheq and nu_cheq[0]
            self.env.cr.execute("UPDATE compta_compteur_cheq_rec SET numcheqrec = %d  WHERE x_exercice_id = %d and company_id = %d" %(self.num_ch_emis,val_ex,val_struct))
        
        
        self.env.cr.execute("""SELECT sum(montant)
        FROM compta_paiement_ordre_line WHERE x_exercice_id = %d AND company_id = %d AND paiement__ordre_id = %d """ %(val_ex, val_struct, id_ordre))
        res = self.env.cr.fetchone()
        self.mnt_ordre_virement = res and res[0]
        val_mnt = self.mnt_ordre_virement

    #Fonction compteur et génération des numéros des ecritures et des lignes d'ecritures
    @api.multi
    def generer_ecriture(self):
        
        self.write({'state': 'P'})
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_ecr = self.no_ecr
        id_ordre = self.id
        var_cptes = int(self.var_cpte)
        vl_mnt = self.mnt_ordre_virement
        val_sens = str(self.fg_sens)
        val_date = self.date_emis
        

        #Attribution des numero et lignes d'ecritures pour l'enregistrement des ordres de virement
        
        self.env.cr.execute("""SELECT count(l.id) from compta_paiement_ordre_line l where l.paiement__ordre_id = %d and l.company_id = %d and l.x_exercice_id = %d and l.retenue = True""" %(id_ordre, val_struct, val_ex ))
        res = self.env.cr.fetchone()
        resu = res and res[0] or 0   

        if resu > 0:
            raise ValidationError(_("Il existe au moins une retenue. Veuillez la ou les traiter avant de poursuivre votre opération."))
        else:
        
            self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
            noecr = self.env.cr.dictfetchall()
            no_ecrs = noecr and noecr[0]['no_ecr']
            no_ecrs1 = noecr and noecr[0]['no_lecr']
            no_ecr = no_ecrs
           
            if not(no_ecr):           
                self.no_ecr = 1
                no_ecrs1 = 0
                for record in self.x_line_ids:
                    no_ecrs1 = no_ecrs1 + 1
                    record.no_lecr = no_ecrs1 
                self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
            else:
                self.no_ecr = no_ecr + 1
                no_ecrs11 = no_ecrs1 + 1
                no_ecrs1= no_ecrs11
                for record in self.x_line_ids:           
                    no_ecrs1 = no_ecrs1 + 1
                    record.no_lecr = no_ecrs1 
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
            for record in self.x_line_ids:
                val = (self.no_ecr)
                val_id = (self.id)
                self.env.cr.execute("UPDATE compta_paiement_ordre_line SET no_ecr = %s WHERE paiement__ordre_id = %s" ,(val, val_id))
            
            self.env.cr.execute("select * from compta_paiement_ordre where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_ordre))
            curs_paiement_ordre = self.env.cr.dictfetchall()
            no_ecrs = curs_paiement_ordre and curs_paiement_ordre[0]['no_ecr']
            no_ecr = int(no_ecrs)
            typ_jr = curs_paiement_ordre and curs_paiement_ordre[0]['type_journal']
            print("jouranl", typ_jr)
            typ_ecr = curs_paiement_ordre and curs_paiement_ordre[0]['type_ecriture']
            print("ecriture", typ_ecr)
            
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, '%s', %s, %s, 'BI', %s, %s, 'P')" %(no_ecr, val_date, typ_ecr, typ_jr, val_ex, val_struct))
    
            self.env.cr.execute("select * from compta_paiement_ordre_line where x_exercice_id = %d and company_id = %d and paiement__ordre_id = %d " %(val_ex,val_struct, id_ordre))
            curs = self.env.cr.dictfetchall()
            
            var_ecr = self.no_ecr
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'P') """ ,(var_ecr,no_ecrs11, var_cptes, vl_mnt,val_ex, val_struct, val_sens, val_date))
               
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, ref_pj, mt_lecr, type_pj, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            SELECT no_ecr, no_lecr , id_imput, ref_pj, montant, type_pj, x_exercice_id, company_id, fg_sens, date_emis, fg_etat
            FROM compta_paiement_ordre_line WHERE x_exercice_id = %d AND company_id = %d AND paiement__ordre_id = %d """ %(val_ex, val_struct, id_ordre))
    
            
            for vals in self.x_line_ids:
                val = vals.ref_pj
                if vals.type_pj.libelle.refe == '31':
                    self.env.cr.execute("update budg_mandat set state = 'F' where x_exercice_id = %s and company_id = %s and no_mandat = %s" ,(val_ex, val_struct, val))
                elif vals.type_pj.libelle.refe == '30':
                    self.env.cr.execute("update budg_op set et_doss = 'F' where x_exercice_id = %s and company_id = %s and no_op = %s" ,(val_ex, val_struct, val))
                
                self.env.cr.execute("select count(id) from compta_retenue where x_exercice_id = %d and company_id = %d and numord = %d" %(val_ex,val_struct, id_ordre))
                re = self.env.cr.fetchone()
                resultat = re and re[0] or 0
                if resultat != 0:
                    
                    self.env.cr.execute("select * from compta_retenue where x_exercice_id = %d and company_id = %d and numord = %d" %(val_ex,val_struct, id_ordre))
                    res1 = self.env.cr.dictfetchall()
                    
                    mnt = res1 and res1[0]['mnt_retenue']
                    typ_pj = res1 and res1[0]['mnt_retenue']
                    typ_ecr = res1 and res1[0]['type_ecriture']
                    typ_op = res1 and res1[0]['typ_op']
                    pj = res1 and res1[0]['ty_pj']
                    ref = res1 and res1[0]['ref_pj']
                    an = res1 and res1[0]['anne_pj']
                    dt = res1 and res1[0]['dte']
                    var_cpt = res1 and res1[0]['id_imput']
                    code1 = res1 and res1[0]['code1']
                    code2 = res1 and res1[0]['code2']
                    
                    self.env.cr.execute("select no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
                    
                    ecr = self.env.cr.fetchone()
                    no_lecrs1 = ecr and ecr[0] or 0
                    no_lecrs1 = no_lecrs1 + 1
                                
                    self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_op ,x_exercice_id, company_id, state) VALUES (%s, '%s', %s, 'BE', %s, %s, 'P')" %(no_ecr, dt, typ_ecr, val_ex, val_struct))
            
                    v_lblecr = 'BO' + '-' + 'C' + '-' + str(code1) + '-' + str(code2) + '-' + str(self.x_exercice_id.no_ex) + '-' + str(ref)
                    print('libelle', v_lblecr)
            
                    self.env.cr.execute("""INSERT INTO compta_ligne_ecriture (no_ecr,no_lecr, no_souscptes, lb_lecr, type_pj, ref_pj, mt_lecr, x_exercice_id, company_id, dt_ligne, fg_sens,fg_etat) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'C', 'P') """ , (var_ecr, no_lecrs1, var_cpt, v_lblecr, pj, ref, mnt, val_ex, val_struct, dt))
                
                        
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_lecrs1,val_ex,val_struct))


    
#classe ordre de paiement lignes
class ComptaOrdrePaiementLine(models.Model):

    _name = "compta_paiement_ordre_line"
    
    no_ecr = fields.Integer()
    no_lecr = fields.Integer("N° Lignes", readonly=True)
    paiement__ordre_id = fields.Many2one("compta_paiement_ordre", ondelete='cascade')
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération", required = False)
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Nature d'opération", required = False)
    type2_operation = fields.Many2one("compta_reg_op_banque_unique", "Type d'opération")
    nature_id = fields.Many2one("compta_table_listnat", 'Nature détaillée')
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", domain = [('code', '=like', 'D%')], required=True)
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1), ('fg_ch_emis','=',True)]", required=True)
    code2 = fields.Char()
    #nature_id = fields.Selection(selection ='test', string='Nature détaillée')
    id_imput = fields.Integer()
    no_imputation = fields.Char()
    date_emis = fields.Date(default=fields.Date.context_today)
    montant = fields.Integer("Montant", required = True)
    type_pj = fields.Many2one('compta_piece_line', 'Pièces Just.', required = True)
    type_pj1 = fields.Selection([
        ('M', 'Mandat'),
        ('OP', 'Ordre de paiement')
        ], 'Pièce Just.', required=False)
    annee_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="An. PJ")
    ref1_pj = fields.Many2one('budg_mandat',"Ref. MDT",domain=[('state', '=', 'E')])
    ref_pj = fields.Char("Ref. PJ", required=True)
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),], 'Sens', default = 'D')
    fg_etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Vérifié'),
        ('R', 'Rejété')], 'Etat', default= 'P')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    retenue = fields.Boolean("Retenue ?")

    @api.onchange('ref1_pj')
    def MontantMandat(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_mdt = int(self.ref1_pj.id)
        
        self.env.cr.execute("""select mnt_ord from budg_mandat where id = %d and
        company_id = %d and x_exercice_id = %d""" %(val_mdt, val_struct, val_ex))
        res = self.env.cr.fetchone()
        res1 = res and res[0] or 0
        
        for val in self:
            if self.ref1_pj:
                self.montant = res1
        
  
    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2 :
                val.code2 = val.type2.type_opcpta1


    @api.onchange('type2','type1')
    @api.model
    def get_imputation_ordre(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1.id)
        val_type2 = str(self.code2)
        #val_idtlv = int(self.id_tlv.id)
        #print('val id',val_idtlv)
        #val_type22 = str(self.type2_op.id.type2_op)
       
        #self.env.cr.execute("""select R.souscompte_id, R.fg_term from  compta_reg_op_guichet_unique R where R.type1_opcpta = %d and R.id = %d and R.x_exercice_id = %d and R.company_id = %d""" %(val_type1,val_type2, val_ex, val_struct))
        #Nouvelle requete
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from compta_type_op_cpta r where r.typebase_id = %s and type_opcpta1 = %s""" ,(val_type1,val_type2))
        #self.env.cr.execute("""select C.id, C.souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        #self.env.cr.execute("""select CD_NAT, LB_NAT, LV_NAT FROM "+" V_NM_TLV +" WHERE " + V_WH_TLV .concate_souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.no_imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        if val_type1 != False and val_type2 != False:
            
            if terminal == 'T':  
                #self.id_imput = imput and imput[0]["id"]
                self.id_imput = imput and imput[0]["souscompte_id"]
                #self.no_imputation = imput and imput[0]["souscpte"]
                #print('la valeur de limput',self.no_imputation)
            else:
                if val_type2 != False:                                       
                    self.env.cr.execute("""select nm_listnat, clause_where from compta_table_listnat where id = 1 """ )
                    res = self.env.cr.dictfetchall()
                    nom_vue = res and res[0]["nm_listnat"]
                    clause_w = res and res[0]["clause_where"] 
                    #self.env.cr.execute("select cd_nat, lb_nat from %s where  %s" %(nom_vue,clause_w))
                    #nature = self.env.cr.dictfetchall()
                    #return [(x.cd_nat, x.lb_nat) for x in nature]
                    #print('valeur nature',nature)
            #return nature
                    #nature = self.env['compta_colonne_caisse'].search([])
                    #return [(x.cd_col_caise, x.lb_court) for x in nature]
                    #self.no_imputation = nature and nature[0]["vl_nat"]
                    #print('la val imputation',self.no_imputation)
    #id_tlv = fields.Selection(selection = get_imputation, string= 'Nature éventuelle')
        


class Compta_releve(models.Model):
    _name = 'compta_releve'
    _rec_name = 'no_releve'
    
    intbanq = fields.Many2one("compta_comptebanque", string = 'Intitulé banque', required=True)
    numcpte = fields.Char("Numéro compte", readonly=True)
    no_releve = fields.Char("N° Rélevé", readonly=True)
    dt_releve = fields.Date("Date du releve", required = True)
    releve_lines = fields.One2many("compta_releve_line", "releve_id", string = 'Lignes de relevés')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    etat = fields.Selection([
        ('N', 'Nouveau'),
        ('C', 'Confirmé'),
        ('V', 'Validé')], 'Etat', default='N')
    
    @api.onchange('intbanq')
    def remplir_compte(self):
        self.numcpte = self.intbanq.num_compte
        
        
    @api.multi
    def action_releve_confirmer(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select noreleve from compta_compteur_releve where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct) )
        avis = self.env.cr.fetchone()
        noreleve = avis and avis[0] or 0
        c1 = int(noreleve) + 1
        c = str(noreleve)
        if c == "0":
            ok = str(c1).zfill(4)
            self.no_releve = ok
            vals = c1
            self.env.cr.execute("""INSERT INTO compta_compteur_releve(x_exercice_id,company_id,noreleve)  VALUES(%d ,%d, %d)""" %(val_ex, val_struct,vals))    
        else:
            c1 = int(noreleve) + 1
            c = str(noreleve)
            ok = str(c1).zfill(4)
            self.no_releve = ok
            vals = c1
            self.env.cr.execute("UPDATE compta_compteur_releve SET noreleve = %d WHERE x_exercice_id = %d and company_id = %d" %(vals, val_ex, val_struct))
    
        self.write({'etat': 'C'})
    
    
class Compta_releveLine(models.Model):
    _name = 'compta_releve_line'
    
    releve_id = fields.Many2one("compta_releve", ondelete='cascade')
    no_releve = fields.Char("Relevé")
    date_releve = fields.Date("Date relevé")
    fg_ecr = fields.Boolean("Ecriture faite ?")
    mnt_delta_c = fields.Float()
    mnt_delta_d = fields.Float()
    mnt_solde = fields.Float()
    mnt_solde_bq = fields.Float("Montant solde")
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit')], 'Sens')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_Compteur_Releve(models.Model):
    
    _name = "compta_compteur_releve"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    noreleve = fields.Integer(default = 0)

class Compta_op_releve(models.Model):
    _name = 'compta_op_releve'
    _rec_name = 'releve_id'
    
    id_cpte_bq = fields.Many2one("compta_comptebanque", string = 'Intitulé Compte', required=True)
    releve_id = fields.Many2one("compta_releve", string = "Rélevé", required=True,domain=[('etat', '=', 'C')])
    numcpte = fields.Char("Numéro compte", readonly=True)
    date_emis = fields.Date("Date")
    montant_recette = fields.Float("Montant Recettes", readonly = True)
    montant_depense = fields.Float("Montant Dépenses", readonly = True)
    nbre_op_recette = fields.Integer("Nbres Op. Recettes", readonly = True)
    nbre_op_depense = fields.Integer("Nbres Op. Dépenses", readonly = True)
    op_releve_lines = fields.One2many("compta_op_releve_lines", "op_releve_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    id_imput = fields.Char()
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture', default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'B')]))
    type_journal = fields.Many2one("compta_type_journal", 'Type journal', default=lambda self: self.env['compta_type_journal'].search([('type_journal','=', 'JB')]))
    var_jr = fields.Integer()
    mnt_total = fields.Integer()
    date_emis = fields.Date("Emis le",default=fields.Date.context_today)
    var_cpte = fields.Integer()
    type_op = fields.Char(default = 'BO')
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Confirmé'),
        ('P', 'Provisoire'),
        ], string ="Etat", default ='draft', required=True)
        
    
    
    @api.onchange('id_cpte_bq')
    def remplir_compte(self):
        self.numcpte = self.id_cpte_bq.num_compte
        self.var_cpte = self.id_cpte_bq.no_imputation.souscpte.id
        
    @api.multi
    def action_confirmer(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_rel = int(self.releve_id)
        val_date = self.date_emis
        typ_jr  = int(self.type_journal)
        typ_ecr = int(self.type_ecriture)
        v_id = int(self.id)
        v_e = "E"
        v_d = "D"
        
        self.env.cr.execute("""select 
        coalesce (sum(case when l.code1 like %s then l.montant end),0) as mntdebit,
        coalesce(sum(case when l.code1 like %s then l.montant end),0) as mntcredit, 
        coalesce (count(case when l.code1 like %s then l.montant end),0) as nbredebit,
        coalesce(count(case when l.code1 like %s then l.montant end),0) as nbrecredit
        from compta_releve r, compta_op_releve_lines l  
        where l.op_releve_id = %s and l.x_exercice_id = %s and l.company_id = %s """ ,(v_d, v_e, v_d ,v_e, v_id, v_ex, v_struct))
       
        res1 = self.env.cr.dictfetchall()
        self.montant_depense = res1 and res1[0]['mntdebit']
        self.nbre_op_depense = res1 and res1[0]['nbredebit']
        self.montant_recette = res1 and res1[0]['mntcredit']
        self.nbre_op_recette = res1 and res1[0]['nbrecredit']
        
        self.write({'state': 'C'})
        
    @api.multi
    def generer_ecriture(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_rel = int(self.releve_id)
        val_date = self.date_emis
        typ_jr  = int(self.type_journal)
        typ_ecr = int(self.type_ecriture)
        v_id = int(self.id)
        var_cptes = int(self.var_cpte)
        releve_id = int(self.releve_id)
        
        mnt_dep = int(self.montant_depense)
        mnt_rec = int(self.montant_recette)

    
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_lecr = noecr and noecr[0]['no_lecr']
        
        v_no_lecr = no_lecr - 1
        v_no_ecr = no_ecrs - 1
        if mnt_dep > 0:
            v_no_ecr = v_no_ecr + 1
            v_no_ecr_D = v_no_ecr
            
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BO', %s, %s, 'P')" ,(v_no_ecr_D, val_date, typ_ecr, typ_jr, val_ex, val_struct))
            
            v_no_lecr = no_lecr + 1
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, 'C', %s, 'P') """ ,(v_no_ecr_D,v_no_lecr, var_cptes, mnt_dep ,val_ex, val_struct, val_date))
            
            self.env.cr.execute("""INSERT INTO compta_r_op_lecr(id_op, ty_op, no_lecr, x_exercice_id, company_id) VALUES(%s,'BO',%s, %s, %s)""",(v_id, v_no_lecr, val_ex, val_struct ))
        
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_D, v_no_lecr,val_ex,val_struct))

        
        if mnt_rec > 0:
            v_no_ecr = v_no_ecr + 1
            v_no_ecr_E = v_no_ecr
            
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BO', %s, %s, 'P')" ,(v_no_ecr_E, val_date, typ_ecr, typ_jr, val_ex, val_struct))
            
            v_no_lecr = no_lecr + 1
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, 'D', %s, 'P') """ ,(v_no_ecr_E,v_no_lecr, var_cptes, mnt_rec ,val_ex, val_struct, val_date))
            
            self.env.cr.execute("""INSERT INTO compta_r_op_lecr(id_op, ty_op, no_lecr, x_exercice_id, company_id) VALUES(%s,'BO',%s, %s, %s)""",(v_id, v_no_lecr, val_ex, val_struct ))
        
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_E, v_no_lecr,val_ex,val_struct))

        self.env.cr.execute("""SELECT code1,id_imput, montant, type_pj FROM compta_op_releve_lines 
        WHERE x_exercice_id = %d AND company_id = %d AND op_releve_id = %d """ %(val_ex, val_struct, v_id))
          
        
        for line in self.env.cr.dictfetchall():
            
            var_cptes = line['id_imput']
            mnt = line['montant']
            pj = line['type_pj']
            code = line['code1']
            
            self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
            noecr = self.env.cr.dictfetchall()
            no_ecrs = noecr and noecr[0]['no_ecr']
            no_lecr = noecr and noecr[0]['no_lecr']
            
            v_no_lecr = no_lecr + 1
            v_no_ecr_E = no_ecrs
            v_no_ecr_D = no_ecrs
            
            if (code[0:1]) == 'E':
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, type_pj, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'C', %s, 'P') """ ,(v_no_ecr_E,v_no_lecr, pj, var_cptes, mnt ,val_ex, val_struct, val_date))
                
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_E, v_no_lecr,val_ex,val_struct))

            else:
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, type_pj, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'D', %s, 'P') """ ,(v_no_ecr_D,v_no_lecr, pj, var_cptes, mnt ,val_ex, val_struct, val_date))
  
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_D, v_no_lecr,val_ex,val_struct))

            self.env.cr.execute("""INSERT INTO compta_r_op_lecr(id_op, ty_op, no_lecr, x_exercice_id, company_id) VALUES(%s,'BO',%s, %s, %s)""",(v_id, v_no_lecr, val_ex, val_struct )) 
            

        self.env.cr.execute("UPDATE compta_releve SET etat = 'V' WHERE id = %d and x_exercice_id = %d AND company_id = %d " %(releve_id,val_ex, val_struct))

        self.write({'state': 'P'})
            
    
    @api.multi
    def generer_ecriture_old(self):
        
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_ecr = self.no_ecr
        id_releve = self.id
        var_cptes = int(self.var_cpte)
        vl_mnt = self.mnt_total
        val_sens = str(self.fg_sens)
        val_date = self.date_emis
        releve_id = int(self.releve_id)
        

        #Attribution des numero et lignes d'ecritures pour l'enregistrement des cheques emis 
 
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
       
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.x_line_ids:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            no_ecrs11 = no_ecrs1 + 1
            no_ecrs1= no_ecrs11
            for record in self.op_releve_lines:           
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
        for record in self.op_releve_lines:
            val = (self.no_ecr)
            val_id = (self.id)
            self.env.cr.execute("UPDATE compta_op_releve_lines SET no_ecr = %s WHERE op_releve_id = %s" ,(val, val_id))
        
        self.env.cr.execute("select * from compta_op_releve where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_ordre))
        curs_op_releve = self.env.cr.dictfetchall()
        no_ecrs = curs_op_releve and curs_op_releve[0]['no_ecr']
        no_ecr = int(no_ecrs)
        typ_jr = curs_op_releve and curs_op_releve[0]['type_journal']
        typ_ecr = curs_op_releve and curs_op_releve[0]['type_ecriture']
        
        self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id) VALUES (%s, %s, %s, %s, 'BO', %s, %s)" ,(no_ecr, val_date, typ_ecr, typ_jr, val_ex, val_struct))

        self.env.cr.execute("select * from compta_op_releve_lines where x_exercice_id = %d and company_id = %d and op_releve_id = %d " %(val_ex,val_struct, id_ordre))
        curs = self.env.cr.dictfetchall()
        
        var_ecr = self.no_ecr
        self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'P') """ ,(var_ecr,no_ecrs11, var_cptes, vl_mnt,val_ex, val_struct, val_sens, val_date))
           
        self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, type_pj, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
        SELECT no_ecr, no_lecr , id_imput, montant, type_pj, x_exercice_id, company_id, fg_sens, date_emis, fg_etat
        FROM compta_op_releve_lines WHERE x_exercice_id = %d AND company_id = %d AND op_releve_id = %d """ %(val_ex, val_struct, id_ordre))

        self.env.cr.execute("UPDATE compta_releve SET etat = 'V' WHERE id = %d and x_exercice_id = %d AND company_id = %d " %(releve_id,val_ex, val_struct))
        
        self.write({'state': 'P'})
    
class Compta_op_releve_lines(models.Model):
    _name = 'compta_op_releve_lines'
    
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    no_lecr = fields.Integer("N° Lignes", readonly=True)
    op_releve_id = fields.Many2one("compta_op_releve", ondelete='cascade')
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération",domain=['|',('code', '=like', 'D%'),('code', '=like', 'E%')], required=True)
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1), ('fg_op_relev','=',True)]", required=True)
    code2 = fields.Char()
    code1 = fields.Char()
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération", required = False)
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Type d'opération", required = False)
    nature_id = fields.Many2one("compta_table_listnat", 'Nature détaillée')
    id_imput = fields.Integer()
    no_imputation = fields.Char()
    montant = fields.Float("Montant", required = True)
    type_pj = fields.Many2one('compta_piece_line', 'Pièce Just.', required = True)
    annee_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="An. PJ")
    ref_pj = fields.Char("Ref. PJ")
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),], 'Sens')
    fg_etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Vérifié'),
        ('R', 'Rejété')], 'Etat', default= 'P')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2 :
                val.code2 = val.type2.type_opcpta1
                
    @api.onchange('type1')
    def Cod1(self):
        for val in self:
            if val.type1 :
                val.code1 = val.type1.code

    @api.onchange('type2','type1')
    @api.model
    def get_imputation_ordre(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1.id)
        val_type2 = str(self.code2)
        #val_idtlv = int(self.id_tlv.id)
        #print('val id',val_idtlv)
        #val_type22 = str(self.type2_op.id.type2_op)
       
        
        #self.env.cr.execute("""select R.souscompte_id, R.fg_term from  compta_reg_op_guichet_unique R where R.type1_opcpta = %d and R.id = %d and R.x_exercice_id = %d and R.company_id = %d""" %(val_type1,val_type2, val_ex, val_struct))
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from compta_type_op_cpta r where r.typebase_id = %s and type_opcpta1 = %s""" ,(val_type1,val_type2))
        #self.env.cr.execute("""select C.id, C.souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.no_imputation = C.souscpte and R.id = %d """ %(val_type1,val_type2))
        #self.env.cr.execute("""select CD_NAT, LB_NAT, LV_NAT FROM "+" V_NM_TLV +" WHERE " + V_WH_TLV .concate_souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.no_imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        if val_type1 != False and val_type2 != False:
            
            if terminal == 'T':  
                #self.id_imput = imput and imput[0]["id"]
                self.id_imput = imput and imput[0]["souscompte_id"]
                #self.no_imputation = imput and imput[0]["souscpte"]
            else:
                if val_type2 != False:                                       
                    self.env.cr.execute("""select nm_listnat, clause_where from compta_table_listnat where id = 1 """ )
                    res = self.env.cr.dictfetchall()
                    nom_vue = res and res[0]["nm_listnat"]
                    print('le nom vue',nom_vue)
                    clause_w = res and res[0]["clause_where"] 
                    print('la clause',clause_w)                  
                    #self.env.cr.execute("select cd_nat, lb_nat from %s where  %s" %(nom_vue,clause_w))
                    #nature = self.env.cr.dictfetchall()
                    #return [(x.cd_nat, x.lb_nat) for x in nature]
                    #print('valeur nature',nature)
            #return nature
                    #nature = self.env['compta_colonne_caisse'].search([])
                    #return [(x.cd_col_caise, x.lb_court) for x in nature]
                    #self.no_imputation = nature and nature[0]["vl_nat"]
                    #print('la val imputation',self.no_imputation)
    #id_tlv = fields.Selection(selection = get_imputation, string= 'Nature éventuelle')
        

class Compta_avis(models.Model):
    _name = 'compta_avis'
    _rec_name = 'no_avis'
    
    intbanq = fields.Many2one("compta_comptebanque", string = 'Intitulé banque', required=True)
    numcpte = fields.Char("Numéro compte", readonly=True)
    no_avis = fields.Char("N° Avis", readonly=True)
    montant = fields.Float("Montant")
    avis_lines = fields.One2many("compta_avis_line", "avis_id", string = 'Lignes des avis')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    etat = fields.Selection([
        ('N', 'Nouveau'),
        ('C', 'Confirmé'),
        ('V', 'Validé'),
        ], 'Etat', default='N')
    #active = fields.Boolean(default = True)

    @api.multi
    def action_avis_confirmer(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_id = self.id
        
        self.env.cr.execute("select noavis from compta_compteur_avis where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct) )
        avis = self.env.cr.fetchone()
        noavis = avis and avis[0] or 0
        c1 = int(noavis) + 1
        c = str(noavis)
        if c == "0":
            ok = str(c1).zfill(4)
            self.no_avis = ok
            vals = c1
            self.env.cr.execute("""INSERT INTO compta_compteur_avis(x_exercice_id,company_id,noavis)  VALUES(%d ,%d, %d)""" %(val_ex, val_struct,vals))    
        else:
            c1 = int(noavis) + 1
            c = str(noavis)
            ok = str(c1).zfill(4)
            self.no_avis = ok
            vals = c1
            self.env.cr.execute("UPDATE compta_compteur_avis SET noavis = %d WHERE x_exercice_id = %d and company_id = %d" %(vals, val_ex, val_struct))
    
        self.write({'etat': 'C'})
        
        self.env.cr.execute("select sum(mnt_solde_bq) from compta_avis_line where avis_id = %d and company_id = %d and x_exercice_id = %d" %(val_id, val_struct, val_ex))
        res = self.env.cr.fetchone()
        self.montant = res and res[0] or 0
    
    @api.onchange('intbanq')
    def remplir_compte(self):
        self.numcpte = self.intbanq.num_compte
    
    
class Compta_avisLine(models.Model):
    _name = 'compta_avis_line'
    
    avis_id = fields.Many2one("compta_avis", ondelete='cascade')
    date_avis = fields.Date("Date")
    fg_ecr = fields.Boolean("Ecriture faite ?")
    mnt_solde_bq = fields.Float("Montant avis")
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit')], 'Sens')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_Compteur_avis(models.Model):
    
    _name = "compta_compteur_avis"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    noavis = fields.Integer(default = 0)

class Compta_op_avis(models.Model):
    _name = 'compta_op_avis'
    _rec_name = 'avis_id'
    
    no_avis = fields.Integer("N° Avis", readonly=True)
    intbanq = fields.Many2one("compta_comptebanque", string = 'Intitulé compte', required=True)
    numcpte = fields.Char("Numéro compte", readonly=True)
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    type_op = fields.Char(default = 'BO')
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture', default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'B')]))
    type_journal = fields.Many2one("compta_type_journal", 'Type journal', default=lambda self: self.env['compta_type_journal'].search([('type_journal','=', 'JB')]))
    var_jr = fields.Integer()
    var_cpte = fields.Integer()
    mnt_total = fields.Float()
    date_emis = fields.Date("Emis le",default=fields.Date.context_today, required = True)
    avis_id = fields.Many2one("compta_avis", string = "Rélevé", required=True)
    montant_recette = fields.Float("Montant Recettes", readonly = True)
    montant_depense = fields.Float("Montant Dépenses", readonly = True)
    nbre_op_recette = fields.Integer("Nbres Op. Recettes",readonly = True)
    nbre_op_depense = fields.Integer("Nbres Op. Dépenses",readonly = True)
    op_avis_lines = fields.One2many("compta_op_avis_lines", "op_avis_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Confirmé'),
        ('P', 'Provisoire'),
        ], string ="Etat", default ='draft', required=True)
    

    @api.onchange('intbanq')
    def remplir_compte(self):
        self.numcpte = self.intbanq.num_compte
        self.var_cpte = self.intbanq.no_imputation.souscpte.id
        
    @api.multi
    def action_confirmer(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_avis = int(self.avis_id)
        val_date = self.date_emis
        typ_jr  = int(self.type_journal)
        typ_ecr = int(self.type_ecriture)
        v_id = int(self.id)
        v_e = "E"
        v_d = "D"
        
        self.env.cr.execute("""select 
        coalesce (sum(case when l.code1 like %s then l.montant end),0) as mntdebit,
        coalesce(sum(case when l.code1 like %s then l.montant end),0) as mntcredit, 
        coalesce (count(case when l.code1 like %s then l.montant end),0) as nbredebit,
        coalesce(count(case when l.code1 like %s then l.montant end),0) as nbrecredit
        from compta_avis r, compta_op_avis_lines l  
        where l.op_avis_id = %s and l.x_exercice_id = %s and l.company_id = %s """ ,(v_d, v_e, v_d, v_e, v_id, v_ex, v_struct))
       
        res1 = self.env.cr.dictfetchall()
        self.montant_depense = res1 and res1[0]['mntdebit']
        self.nbre_op_depense = res1 and res1[0]['nbredebit']
        self.montant_recette = res1 and res1[0]['mntcredit']
        self.nbre_op_recette = res1 and res1[0]['nbrecredit']
        
        self.write({'state': 'C'})
        
    @api.multi
    def generer_ecriture(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_avis = int(self.avis_id)
        val_date = self.date_emis
        typ_jr  = int(self.type_journal)
        typ_ecr = int(self.type_ecriture)
        v_id = int(self.id)
        var_cptes = int(self.var_cpte)
        avis_id = int(self.avis_id)
        
        mnt_dep = int(self.montant_depense)
        mnt_rec = int(self.montant_recette)

    
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_lecr = noecr and noecr[0]['no_lecr']
        
        v_no_lecr = no_lecr - 1
        v_no_ecr = no_ecrs - 1
        if mnt_dep > 0:
            v_no_ecr = v_no_ecr + 1
            v_no_ecr_D = v_no_ecr
            
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BO', %s, %s, 'P')" ,(v_no_ecr_D, val_date, typ_ecr, typ_jr, val_ex, val_struct))
            
            v_no_lecr = no_lecr + 1
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, 'C', %s, 'P') """ ,(v_no_ecr_D,v_no_lecr, var_cptes, mnt_dep ,val_ex, val_struct, val_date))
            
            self.env.cr.execute("""INSERT INTO compta_r_op_lecr(id_op, ty_op, no_lecr, x_exercice_id, company_id) VALUES(%s,'BO',%s, %s, %s)""",(v_id, v_no_lecr, val_ex, val_struct ))
        
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_D, v_no_lecr,val_ex,val_struct))

        
        if mnt_rec > 0:
            v_no_ecr = v_no_ecr + 1
            v_no_ecr_E = v_no_ecr
            
            self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id) VALUES (%s, %s, %s, %s, 'BO', %s, %s)" ,(v_no_ecr_E, val_date, typ_ecr, typ_jr, val_ex, val_struct))
            
            v_no_lecr = no_lecr + 1
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, 'D', %s, 'P') """ ,(v_no_ecr_E,v_no_lecr, var_cptes, mnt_rec ,val_ex, val_struct, val_date))
            
            self.env.cr.execute("""INSERT INTO compta_r_op_lecr(id_op, ty_op, no_lecr, x_exercice_id, company_id) VALUES(%s,'BO',%s, %s, %s)""",(v_id, v_no_lecr, val_ex, val_struct ))
        
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_E, v_no_lecr,val_ex,val_struct))

        self.env.cr.execute("""SELECT code1,id_imput, montant, type_pj FROM compta_op_avis_lines 
        WHERE x_exercice_id = %d AND company_id = %d AND op_avis_id = %d """ %(val_ex, val_struct, v_id))
          
        
        for line in self.env.cr.dictfetchall():
            
            var_cptes = line['id_imput']
            mnt = line['montant']
            pj = line['type_pj']
            code = line['code1']
            
            self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
            noecr = self.env.cr.dictfetchall()
            no_ecrs = noecr and noecr[0]['no_ecr']
            no_lecr = noecr and noecr[0]['no_lecr']
            
            v_no_lecr = no_lecr + 1
            v_no_ecr_D = no_ecrs
            v_no_ecr_E = no_ecrs
            
            if (code[0:1]) == 'E':
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, type_pj, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'C', %s, 'P') """ ,(v_no_ecr_E,v_no_lecr, pj, var_cptes, mnt ,val_ex, val_struct, val_date))
                
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_E, v_no_lecr,val_ex,val_struct))

            else:
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, type_pj, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'D', %s, 'P') """ ,(v_no_ecr_D,v_no_lecr, pj, var_cptes, mnt ,val_ex, val_struct, val_date))
  
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(v_no_ecr_D, v_no_lecr,val_ex,val_struct))

            self.env.cr.execute("""INSERT INTO compta_r_op_lecr(id_op, ty_op, no_lecr, x_exercice_id, company_id) VALUES(%s,'BO',%s, %s, %s)""",(v_id, v_no_lecr, val_ex, val_struct )) 
            

        self.env.cr.execute("UPDATE compta_avis SET etat = 'V' WHERE id = %d and x_exercice_id = %d AND company_id = %d " %(avis_id,val_ex, val_struct))

        self.write({'state': 'P'})

        
        
    
class Compta_op_avis_lines(models.Model):
    _name = 'compta_op_avis_lines'
    
    no_lecr = fields.Integer("N° Lignes", readonly=True)
    op_avis_id = fields.Many2one("compta_op_avis", ondelete='cascade')
    type_operation = fields.Many2one("compta_type1_op_cpta", "Catégorie d'opération", required = False)
    type2_op = fields.Many2one("compta_reg_op_guichet_unique", "Type d'opération", required = False)
    nature_id = fields.Many2one("compta_table_listnat", 'Nature détaillée')
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération",domain=['|',('code', '=like', 'D%'),('code', '=like', 'E%')], required=True)
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1), ('fg_ch_emis','=',True)]", required=True)
    code2 = fields.Char()
    code1 = fields.Char()
    id_imput = fields.Integer()
    no_imputation = fields.Char()
    montant = fields.Float("Montant", required = True)
    type_pj = fields.Many2one('compta_piece_line', 'Pièce Just.', required = True)
    annee_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="An. PJ")
    ref_pj = fields.Char("Ref. PJ", required = True)
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),], 'Sens')
    fg_etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Vérifié'),
        ('R', 'Rejété')], 'Etat', default= 'P')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2 :
                val.code2 = val.type2.type_opcpta1
    
    @api.onchange('type1')
    def Cod1(self):
        for val in self:
            if val.type1 :
                val.code1 = val.type1.code


    @api.onchange('type2','type1')
    @api.model
    def get_imputation_ordre(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1.id)
        val_type2 = str(self.code2)
        #val_idtlv = int(self.id_tlv.id)
        #print('val id',val_idtlv)
        #val_type22 = str(self.type2_op.id.type2_op)
       
        #self.env.cr.execute("""select R.souscompte_id, R.fg_term from  compta_reg_op_guichet_unique R where R.type1_opcpta = %d and R.id = %d and R.x_exercice_id = %d and R.company_id = %d""" %(val_type1,val_type2, val_ex, val_struct))
        #Nouvelle requete
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from compta_type_op_cpta r where r.typebase_id = %s and type_opcpta1 = %s""" ,(val_type1,val_type2))
        #self.env.cr.execute("""select C.id, C.souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        #self.env.cr.execute("""select CD_NAT, LB_NAT, LV_NAT FROM "+" V_NM_TLV +" WHERE " + V_WH_TLV .concate_souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.no_imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        if val_type1 != False and val_type2 != False:
            
            if terminal == 'T':  
                #self.id_imput = imput and imput[0]["id"]
                self.id_imput = imput and imput[0]["souscompte_id"]
                #self.no_imputation = imput and imput[0]["souscpte"]
                #print('la valeur de limput',self.no_imputation)
            else:
                if val_type2 != False:                                       
                    self.env.cr.execute("""select nm_listnat, clause_where from compta_table_listnat where id = 1 """ )
                    res = self.env.cr.dictfetchall()
                    nom_vue = res and res[0]["nm_listnat"]
                    print('le nom vue',nom_vue)
                    clause_w = res and res[0]["clause_where"] 
                    print('la clause',clause_w)                  
                    #self.env.cr.execute("select cd_nat, lb_nat from %s where  %s" %(nom_vue,clause_w))
                    #nature = self.env.cr.dictfetchall()
                    #return [(x.cd_nat, x.lb_nat) for x in nature]
                    #print('valeur nature',nature)
            #return nature
                    #nature = self.env['compta_colonne_caisse'].search([])
                    #return [(x.cd_col_caise, x.lb_court) for x in nature]
                    #self.no_imputation = nature and nature[0]["vl_nat"]
                    #print('la val imputation',self.no_imputation)
    #id_tlv = fields.Selection(selection = get_imputation, string= 'Nature éventuelle')


class Compta_rapprochement(models.Model):
    _name='compta_rapprochement'
    _rec_name = 'intbanq'
    
    intbanq = fields.Many2one("compta_comptebanque","Intitulé compte", required=True)
    numcpte = fields.Char("Numéro compte", readonly=True)
    dt_rappro = fields.Date("A la date du", required=True)
    dt_dernier = fields.Date('Date dernier relevé', required=True)
    nbre_cheq_emis = fields.Integer("Nombre de chèques émis", readonly=True)
    mnt_cheq_emis = fields.Integer("Montant de chèques émis", readonly=True)
    nbre_cheq_recu = fields.Integer("Nombre de chèques réçus", readonly=True)
    mnt_cheq_recu = fields.Integer("Montant de chèques reçus", readonly=True)
    nbre_ov = fields.Integer("Nombre ordres de virement", readonly=True)
    mnt_ov = fields.Integer("Montant ordres de virement", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    @api.onchange('intbanq')
    def remplir_compte(self):
        self.numcpte = self.intbanq.num_compte
        
    
    def chercher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_date = str(self.dt_rappro)
        val_cpte = self.numcpte
        
        self.env.cr.execute("""select coalesce(count(d.id)) as nbr, coalesce(sum(d.mnt_ordre_virement)) as mnt from compta_paiement_dep d 
        where d.x_exercice_id = %s and d.company_id = %s and d.state = 'P' and d.date_emis <= %s
        and d.numcptbanq = %s """, (val_ex, val_struct, val_date, val_cpte))
        line = self.env.cr.dictfetchall()
        self.nbre_cheq_emis = line and line[0]["nbr"]
        self.mnt_cheq_emis = line and line[0]["mnt"]      
        
        
        self.env.cr.execute("""select coalesce(count(o.id)) as nbr, coalesce(sum(o.mnt_ordre_virement)) as mnt from compta_paiement_ordre o
        where o.x_exercice_id = %s and o.company_id = %s and o.state = 'P' and o.date_emis <= %s
        and o.numcptbanq = %s """, (val_ex, val_struct, val_date, val_cpte))
        line1 = self.env.cr.dictfetchall()
        self.nbre_ov = line1 and line1[0]["nbr"]
        self.mnt_ov = line1 and line1[0]["mnt"]     

class Compta_balance(models.Model):
    _name = "compta_balance"

    name = fields.Char(default="Balance arrêtée")    
    periode = fields.Many2one("compta_periode", string="Période")  
    periode_deb = fields.Date("Du", readonly= True)
    periode_fin = fields.Date("Au", readonly= True)
    exercice = fields.Selection([
        ('T', "Tout l'exercice")])
    option = fields.Selection([
        ('Y', "Avec balance d'entrée"),
        ('N', "Sans balance d'entrée"),
        ], string="Option de balance")
    dt_envoi = fields.Date("Date d'envoi")
    dt_reception = fields.Date("Date d'envoi")
    dt_traite = fields.Date("Date d'envoi")
    user_t = fields.Many2one('res.users', string='User traitant', default=lambda self: self.env.user)
    etat = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Validé'),
        ('E', 'Envoyé'),
        ('R', 'Receptionné'),
        ('F', 'Intégré'),
        ], 'Etat', default="draft")
    balance_lines = fields.One2many("compta_balance_detail", "balance_id", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Choisir l'exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
    @api.onchange('periode')
    def periode_on_change(self):

        if self.periode:
            self.periode_deb = self.periode.dt_debut
            self.periode_fin = self.periode.dt_fin
        
    @api.multi
    def action_confirmer(self):
        self.write({'etat': 'N'})
        
    @api.multi
    def action_envoyer(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("""INSERT INTO compta_ligne_balance_global(x_exercice_id, entier, entier_cpte, crediteur, debiteur, company_id)
        SELECT d.x_exercice_id, d.entier, d.entier_cpte, d.crediteur, d.debiteur,  b.company_id
        FROM  compta_balance b, compta_balance_detail d WHERE b.id = d.balance_id AND b.etat = 'N' and b.company_id = %d and b.x_exercice_id = %d order by entier_cpte""" %(val_struct, val_ex)) 
    
        self.write({'etat': 'E'})
        self.dt_envoi = date.today()
        
        
    @api.multi
    def action_receptionner(self):
        self.write({'etat': 'R'})
        self.dt_reception = date.today()
       
    @api.multi
    def action_integrer(self):
        self.write({'etat': 'F'})
        self.dt_traite = date.today()
        
        self.env.cr.execute("""INSERT INTO compta_ligne_balance_global(x_exercice_id, company_id, crediteur, debiteur, origine_structure)
        SELECT d.x_exercice_id,  b.company_id, d.numero_compte, d.crediteur, d.debiteur, 
        FROM  compta_balance b, compta_balance_detail d WHERE b.id = d.balance_id AND b.etat = 'R' """) 
    
    
    def remplir_balance(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_deb = str(self.periode_deb)
        val_fin = str(self.periode_fin)
        
        for vals in self:
            vals.env.cr.execute("""select l.cpte as cpte ,r.id as ids,r.concate_souscpte as compte from ref_souscompte r, compta_plan_line l 
            where r.id = l.souscpte and l.company_id = %d group by r.id, r.concate_souscpte, l.cpte order by compte asc""" %(val_struct))
            
            rows = vals.env.cr.dictfetchall()
            result = []
                
            vals.balance_lines.unlink()
            for line in rows:
                result.append((0,0, {'entier_cpte' : line['cpte'],'entier' : line['ids'],'numero_compte' : line['compte']}))
            self.balance_lines = result
            
            self.CalculMnt()
        
    
    def CalculMnt(self):    
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_deb = str(self.periode_deb)
        val_fin = str(self.periode_fin)
        v_id = int(self.id)
            
        if self.periode and self.option == 'Y':
            self.env.cr.execute("""select l.no_souscptes as ids,
            sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
            sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
            from ref_souscompte r,  compta_ligne_ecriture l
            where r.id = l.no_souscptes and l.dt_ligne between %s and %s
            and l.company_id = %s and l.x_exercice_id = %s and l.fg_etat != 'A' group by l.no_souscptes""" ,(val_deb, val_fin, val_struct, val_ex))
            
            for val in self.env.cr.dictfetchall():
                cpte = val['ids']
                deb = val['debiteur']
                cred = val['crediteur']
                
                self.env.cr.execute("UPDATE compta_balance_detail SET crediteur = %s, debiteur = %s where entier = %s and balance_id = %s and company_id = %s and x_exercice_id = %s" ,(deb,cred, cpte, v_id, val_struct, val_ex))
                
        elif self.periode and self.option == 'N':
            
            self.env.cr.execute("""select l.no_souscptes as ids,
            sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
            sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
            from ref_souscompte r, compta_ligne_ecriture l
            where r.id = l.no_souscptes and l.dt_ligne between %s and %s
            and l.company_id = %s and l.x_exercice_id = %s and l.fg_etat != 'A' l.no_ecr <> 0 group by l.no_souscptes""" ,(val_deb, val_fin, val_struct, val_ex))
            
            for val in self.env.cr.dictfetchall():
                cpte = val['ids']
                deb = val['debiteur']
                cred = val['crediteur']
                
                self.env.cr.execute("UPDATE compta_balance_detail SET crediteur = %s, debiteur = %s where entier = %s and balance_id = %s and company_id = %s and x_exercice_id = %s" ,(deb,cred, cpte, v_id, val_struct, val_ex))
            
        elif self.exercice and self.option == 'Y':
            
            self.env.cr.execute("""select l.no_souscptes as ids,
            sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
            sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
            from ref_souscompte r, compta_ligne_ecriture l
            where r.id = l.no_souscptes
            and l.company_id = %s and l.x_exercice_id = %s and l.fg_etat != 'A' group by l.no_souscptes""" ,(val_struct, val_ex))
            
            for val in self.env.cr.dictfetchall():
                cpte = val['ids']
                deb = val['debiteur']
                cred = val['crediteur']
                
                self.env.cr.execute("UPDATE compta_balance_detail SET crediteur = %s, debiteur = %s where entier = %s and balance_id = %s and company_id = %s and x_exercice_id = %s" ,(deb,cred, cpte, v_id, val_struct, val_ex))
            
        
        elif self.exercice and self.option == 'N':
            
            self.env.cr.execute("""select l.no_souscptes as ids,
            sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
            sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
            from ref_souscompte r, compta_ligne_ecriture l
            where r.id = l.no_souscptes
            and l.company_id = %s and l.x_exercice_id = %s and l.fg_etat != 'A' and l.no_ecr <> 0 group by l.no_souscptes""" ,(val_struct, val_ex))
            
            for val in self.env.cr.dictfetchall():
                cpte = val['ids']
                deb = val['debiteur']
                cred = val['crediteur']
                
                self.env.cr.execute("UPDATE compta_balance_detail SET crediteur = %s, debiteur = %s where entier = %s and balance_id = %s and company_id = %s and x_exercice_id = %s" ,(deb,cred, cpte, v_id, val_struct, val_ex))
            
    
class Compta_balance_detail(models.Model):
    _name = "compta_balance_detail"
    
    balance_id = fields.Many2one("compta_balance", ondelete='cascade')
    entier_cpte = fields.Integer()
    entier = fields.Integer()
    numero_compte = fields.Char("N° et Intitulé de Compte")
    crediteur = fields.Integer("Créditeur")
    debiteur = fields.Integer("Débiteur")
    periode = fields.Many2one("compta_periode", string="Période")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)



class Compta_balance_reel(models.Model):
    _name = "compta_balance_reel"
    
    name = fields.Char("BALANCE EN TEMPS REEL", readonly=True)
    periode_deb = fields.Date("Du", readonly= True)
    periode_fin = fields.Date("Au", default=fields.Date.context_today, readonly = True)
    balance_lines = fields.One2many("compta_balance_reel_detail", "balance_reel_id", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        
        for vals in self:
            vals.env.cr.execute("""select l.cpte as cpte ,r.id as ids,r.concate_souscpte as compte from ref_souscompte r, compta_plan_line l 
            where r.id = l.souscpte and l.company_id = %d group by r.id, r.concate_souscpte,l.cpte order by compte asc""" %(val_struct))
            
            rows = vals.env.cr.dictfetchall()
            result = []
                
            vals.balance_lines.unlink()
            for line in rows:
                result.append((0,0, {'entier_cpte' : line['cpte'],'entier' : line['ids'],'numero_compte' : line['compte']}))
            self.balance_lines = result
            
            self.remplir_balance_reel()
        
                
        
    
    def remplir_balance_reel(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_deb = date(date.today().year,1, 1)
        self.periode_deb = val_deb 
        val_fin = str(self.periode_fin)
        v_id = int(self.id)
    
        
        self.env.cr.execute("""select l.no_souscptes as ids,
        (coalesce(sum( case when l.fg_sens = 'D' then l.mt_lecr end),0)) as debiteur,
        (coalesce(sum( case when l.fg_sens = 'C' then l.mt_lecr end),0)) as crediteur
        from ref_souscompte r, compta_ligne_ecriture l where r.id = l.no_souscptes and l.dt_ligne between %s
        and %s and l.company_id = %s and l.x_exercice_id = %s and l.fg_etat != 'A' and no_ecr <> 0 group by l.no_souscptes""" ,(val_deb, val_fin, val_struct, val_ex))
            
        
        for val in self.env.cr.dictfetchall():
            cpte = val['ids']
            mt_c = val['crediteur']
            mt_d = val['debiteur']
            
            self.env.cr.execute("UPDATE compta_balance_reel_detail SET crediteur = %s, debiteur = %s where entier = %s and balance_reel_id = %s and company_id = %s and x_exercice_id = %s" %(mt_c,mt_d, cpte, v_id, val_struct, val_ex))
    
    
    
class Compta_balance_reel_detail(models.Model):
    _name = "compta_balance_reel_detail"
    
    balance_reel_id = fields.Many2one("compta_balance_reel", ondelete='cascade')
    entier = fields.Integer()
    entier_cpte = fields.Integer()
    numero_compte = fields.Char("N° et Intitulé Compte", readonly=True)
    crediteur = fields.Integer("Créditeur", readonly=True)
    debiteur = fields.Integer("Débiteur", readonly=True)
    periode = fields.Many2one("compta_periode", string="Période")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)



class Compta_balance_entree(models.Model):
    _name="compta_balance_entree"
    _rec_name = "no_ecr"
    
    no_ecr = fields.Integer(string="N° Ecriture", readonly=True)
    montant = fields.Integer("Montant")
    dte = fields.Date(string="Date",default=fields.Date.context_today, readonly=True)
    #type_journal = fields.Many2one("compta_type_journal",states={'P': [('readonly', True)]},default=lambda self: self.env['compta_type_journal'].search([('type_journal','=', 'JB')]))
    type_ecriture = fields.Many2one("compta_type_ecriture",default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'F')]))
    etat = fields.Selection([
        ('draft', 'Brouillon'),
        ('V', 'Validé'),
        ('P', 'Provisoire'),
        ], 'Etat', default="draft")
    entree_line = fields.One2many('compta_balance_entree_line', 'entree_id' )
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    @api.multi
    def valider_balance(self):
        val_struct = int(self.company_id)
        
        self.env.cr.execute("""select count(id) from compta_balance_entree where company_id = %d""" %(val_struct))
        nbr = self.env.cr.fetchone()
        nbre = nbr and nbr[0] or 0
        if nbre > 1:
            raise ValidationError(_("La balance d'entrée ne peut êre saisie qu'une seule fois."))
        
        self.write({'etat': 'V'})
        
        
    @api.multi
    def gen_balance(self):
        
        self.write({'etat': 'P'})
       
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = self.id
        val_date = self.dte
     
        #Attribution des numero et lignes d'ecritures pour l'enregistrement
 
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
       
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.entree_line:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            no_ecrs11 = no_ecrs1 + 1
            no_ecrs1= no_ecrs11
            for record in self.entree_line:           
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(record.no_lecr,val_ex,val_struct))
        
        #for record in self.entree_line:
        #    val_id = (self.id)
        #    self.env.cr.execute("UPDATE compta_balance_entree_line SET no_ecr = 0 WHERE entree_id = %s" ,(v_id))
        
        self.env.cr.execute("SELECT type_ecriture FROM compta_balance_entree WHERE x_exercice_id = %d and company_id = %d" %(val_ex,val_struct))
        res = self.env.cr.fetchone()
        val_ecr = res and res[0]
        self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_op ,x_exercice_id, company_id, state) VALUES (0, %s, %s, 'L', %s, %s, 'P')" ,(val_ecr, val_date, val_ex, val_struct))

        #self.env.cr.execute("select r.no_imputs from compta_regle_simplifie r where x_exercice_id = %s and company_id = %s AND cd_rg_unique = 'BE' " ,(val_ex,val_struct))     
        #res = self.env.cr.fetchone()
        #val = res and res[0]

        self.env.cr.execute("select * from compta_balance_entree_line where x_exercice_id = %s and company_id = %s and entree_id = %s " ,(val_ex,val_struct, v_id))     
        
        for line in self.env.cr.dictfetchall():
            
            v_lecr = line['no_lecr']
            v_cpte = line['cptes']
            v_mnt = line['montant']
            v_sens = line['fg_sens']
            v_date = line['date_emis']
            v_etat = line['fg_etat']
            var_ecr = 0
            
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """ ,(var_ecr, v_lecr, v_cpte, v_mnt, val_ex, val_struct, v_sens, v_date, v_etat))
        
        
            if v_sens == 'C':
                val_sens = 'D'
            else:
                val_sens = 'C'
            
            
            #self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            #VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""" ,(var_ecr, v_lecr, val, v_mnt, val_ex, val_struct, val_sens, v_date, v_etat))
              
            
            
class Compta_balance_entree_line(models.Model):
    _name = "compta_balance_entree_line"
    
    entree_id = fields.Many2one("compta_balance_entree", ondelete='cascade')
    no_lecr = fields.Integer("N° Lignes", readonly=True)
    cpte = fields.Many2one("compta_plan_line", "Compte   ", required=True)
    cptes = fields.Integer()
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crébit'),
        ], string="Sens", required=True)
    montant = fields.Float("Montant", required=True)
    date_emis = fields.Date(default=fields.Date.context_today)
    fg_etat = fields.Char("Etat", default='V')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    @api.onchange('cpte')
    def Onchangecpte(self):
        
        if self.cpte:
            self.cptes = self.cpte.souscpte.id

class Compta_balance_global(models.Model):
    _name = "compta_balance_global"
    
    periode = fields.Many2one("compta_periode")  
    etat = fields.Selection([
        ('N', 'Nouveau'),
        ('I', 'Intégré'),
        ('R', 'Receptionné'),
        ('F', 'Traité'),
        ], 'Etat')
    balance_global_lines = fields.One2many("compta_balance_global_detail", "balance_global_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    @api.multi
    def action_nouveau(self):
        self.write({'etat': 'N'})
        
    @api.multi
    def action_integrer(self):
        self.write({'etat': 'I'})

    @api.multi
    def action_receptionner(self):
        self.write({'etat': 'R'})
        
    @api.multi
    def action_traiter(self):
        self.write({'etat': 'F'})
        
class Compta_balance_global_detail(models.Model):
    _name = 'compta_balance_global_detail'
    
    balance_global_id = fields.Many2one("compta_balance_global", ondelete='cascade')
    numero_compte = fields.Char("N° Compte")
    intitule_compte = fields.Char("Intitulé")
    crediteur = fields.Integer("Créditeur")
    debiteur = fields.Integer("Débiteur")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_ligne_balance_global(models.Model):
    _name = 'compta_ligne_balance_global'
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    periode = fields.Many2one("compta_periode", string="Période", readonly=True)
    numero_compte = fields.Char("N° Compte", readonly=True)
    entier = fields.Many2one("ref_souscompte", "Sous compte")
    entier_cpte = fields.Many2one("ref_compte", "Compte")
    crediteur = fields.Integer("Créditeur", readonly=True)
    debiteur = fields.Integer("Débiteur", readonly=True)
    

class Compta_retour_balance(models.Model):
    _name='compta_retour_balance'
    
    balance_id = fields.Many2one("compta_balance", string="Choisir la balance")
    
  
class Compta_correction_ligne(models.Model):
    _name='compta_correction_ligne'
    
    type_correction = fields.Selection([
        ('EM', 'Erreur montant'),
        ('EP', 'Erreur piece. just'),
        ('EC', 'Erreur compte'),
        ('AL', 'Annulation ligne '),
        ], "Type de correction", required=True)
    cpte = fields.Many2one("compta_verif_ligne", "Compte")
    compte = fields.Many2one("compta_teneur_compte_line", required=True)
    noecr = fields.Char("N° Ecriture" ,readonly=True)
    nolecr = fields.Char("N° Ligne",readonly=True)
    libelle = fields.Char("Libellé",readonly=True)
    sens = fields.Char("Sens",readonly=True)
    montant = fields.Integer("Montant",readonly=True)
    type_pj = fields.Char("Type PJ",readonly=True)
    motif = fields.Text('Motif rejet',readonly=True)
    new_montant = fields.Integer("Nouveau Montant")
    new_pj = fields.Many2one("ref_piece_justificatives", 'Nouvelle pièce')
    new_ref_pj = fields.Char("Référence")
    new_compte = fields.Many2one("compta_plan_line", "Nouveau compte")
    new_comptes = fields.Integer()
    teneur = fields.Many2one('compta_teneur_compte', string='Teneur de compte', domain="[('teneur','=', user_id)]", required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)



    @api.onchange('cpte')
    def OnChange_Cpte(self):
        
        for val in self:
            if self.cpte:
                self.correction_ligne_line = self.cpte.verif_ligne_line


class ComptaErreurPj(models.Model):
    _name = "compta_erreur_pj"
    
    name = fields.Char("Nom", default="Erreur Pièce Justificative")
    compte = fields.Many2one("compta_teneur_compte_line", required=True)
    id_compte = fields.Integer()
    teneur = fields.Many2one('compta_teneur_compte', string='Teneur de compte', domain="[('teneur','=', user_id)]", required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)
    erreur_pj_line = fields.One2many("compta_erreur_pj_line", "erreur_pj_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    
    @api.onchange("compte")
    def ChangeCompte(self):
        if self.compte:
            self.id_compte = self.compte.compte.souscpte.id
            
    def chercher(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_cpte = int(self.id_compte)
        
        for vals in self:
            vals.env.cr.execute("""select distinct l.no_ecr as noecr, l.no_lecr as ligne, l.lb_lecr as libelle, l.type_pj as piece,
            l.fg_sens as sens , l.mt_lecr as montant from compta_ligne_ecriture l, ref_souscompte r
            where r.id = l.no_souscptes and l.no_souscptes = %s and l.fg_etat = 'P' 
            and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""" ,(v_cpte, v_ex, v_struct))
            
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.erreur_pj_line.unlink()
            for line in rows:
                result.append((0,0, {'noecr' : line['noecr'], 'nolecr': line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant'], 'type_pj': line['piece']}))
            self.erreur_pj_line = result
    
    def corriger(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_id = int(self.id)
        
        self.env.cr.execute("select * from compta_erreur_pj_line where erreur_pj_id = %d and company_id = %d and x_exercice_id = %d" %(v_id, v_struct, v_ex))
        for x in self.env.cr.dictfetchall():
            ecr = x['noecr']
            lecr = x['nolecr']
            cor = x['corrige']
            pj = x['new_pj']
            an = x['an_pj']
            ref = x['new_ref_pj']
            
            if cor == True:
  
                self.env.cr.execute("UPDATE compta_ligne_ecriture SET piece_id = %s, ref_pj = %s, x_exercice_id = %s WHERE company_id = %s and x_exercice_id = %s and no_ecr = %s and no_lecr = %s" ,(pj, ref, an, v_struct, v_ex, ecr, lecr))
    
        
        

class ComptaErreurPjLine(models.Model):
    _name = "compta_erreur_pj_line"
    
    erreur_pj_id = fields.Many2one("compta_erreur_pj", ondelete='cascade')
    noecr = fields.Integer("N° Ecriture" ,readonly=True)
    nolecr = fields.Integer("N° Ligne",readonly=True)
    libelle = fields.Char("Libellé",readonly=True)
    sens = fields.Char("Sens",readonly=True)
    montant = fields.Integer("Montant",readonly=True)
    type_pj = fields.Many2one("compta_piece_line", "Pièce",readonly=True)
    new_pj = fields.Many2one("ref_piece_justificatives", 'Nouvelle pièce', required=False)
    new_ref_pj = fields.Char("Ref Pièce")
    an_pj = fields.Many2one("ref_exercice", string="An PJ")
    corrige = fields.Boolean("Crg ?")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)



class ComptaErreurMnt(models.Model):
    _name = "compta_erreur_mnt"
    
    name = fields.Char("Nom", default="Erreur Montant")
    compte = fields.Many2one("compta_teneur_compte_line", required=True)
    teneur = fields.Many2one('compta_teneur_compte', string='Teneur de compte', domain="[('teneur','=', user_id)]", required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)
    id_compte = fields.Integer()
    erreur_mnt_line = fields.One2many("compta_erreur_mnt_line", "erreur_mnt_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    
    @api.onchange("compte")
    def ChangeCompte(self):
        if self.compte:
            self.id_compte = self.compte.compte.souscpte.id
            
    def chercher(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_cpte = int(self.id_compte)
        
        for vals in self:
            vals.env.cr.execute("""select distinct l.no_ecr as noecr, l.no_lecr as ligne, l.lb_lecr as libelle,
            l.fg_sens as sens , l.mt_lecr as montant from compta_ligne_ecriture l, ref_souscompte r
            where r.id = l.no_souscptes and l.no_souscptes = %s and l.fg_etat = 'R' 
            and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""" ,(v_cpte, v_ex, v_struct))
            
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.erreur_mnt_line.unlink()
            for line in rows:
                result.append((0,0, {'noecr' : line['noecr'], 'nolecr': line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant']}))
            self.erreur_mnt_line = result
    
    def corriger(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_id = int(self.id)
        
        self.env.cr.execute("select * from compta_erreur_mnt_line where erreur_mnt_id = %d and company_id = %d and x_exercice_id = %d" %(v_id, v_struct, v_ex))
        for x in self.env.cr.dictfetchall():
            ecr = x['noecr']
            lecr = x['nolecr']
            mnt = x['new_mnt']
            
            self.env.cr.execute("UPDATE compta_ligne_ecriture SET mt_lecr = %s, fg_etat = 'P' WHERE company_id = %s and x_exercice_id = %s and no_ecr = %s and no_lecr = %s" ,(mnt, v_struct, v_ex, ecr, lecr))
    

class ComptaErreurMntLine(models.Model):
    _name = "compta_erreur_mnt_line"
    
    erreur_mnt_id = fields.Many2one("compta_erreur_mnt", ondelete='cascade')
    noecr = fields.Integer("N° Ecriture" ,readonly=True)
    nolecr = fields.Integer("N° Ligne",readonly=True)
    libelle = fields.Char("Libellé",readonly=True)
    sens = fields.Char("Sens",readonly=True)
    montant = fields.Integer("Montant",readonly=True)
    new_mnt = fields.Float("Mnt voulu", required=False)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)

    
class ComptaErreurCpt(models.Model):
    _name = "compta_erreur_cpt"
    
    name = fields.Char("Nom", default="Erreur Compte")
    compte = fields.Many2one("compta_teneur_compte_line", required=True)
    id_compte = fields.Integer()
    teneur = fields.Many2one('compta_teneur_compte', string='Teneur de compte', domain="[('teneur','=', user_id)]", required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)
    erreur_cpt_line = fields.One2many("compta_erreur_cpt_line", "erreur_cpt_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    
    @api.onchange("compte")
    def ChangeCompte(self):
        if self.compte:
            self.id_compte = self.compte.compte.souscpte.id
    
    def chercher(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_cpte = int(self.id_compte)
        
        for vals in self:
            vals.env.cr.execute("""select distinct l.no_ecr as noecr, l.no_lecr as ligne, l.lb_lecr as libelle, l.no_souscptes as cpte,
            l.fg_sens as sens , l.mt_lecr as montant from compta_ligne_ecriture l, ref_souscompte r
            where r.id = l.no_souscptes and l.no_souscptes = %s and l.fg_etat = 'R' 
            and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""" ,(v_cpte, v_ex, v_struct))
            
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.erreur_cpt_line.unlink()
            for line in rows:
                result.append((0,0, {'noecr' : line['noecr'], 'nolecr': line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant'], 'compte': line['cpte']}))
            self.erreur_cpt_line = result
    
    
    def corriger(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_id = int(self.id)
        
        self.env.cr.execute("select * from compta_erreur_cpt_line where erreur_cpt_id = %d and company_id = %d and x_exercice_id = %d" %(v_id, v_struct, v_ex))
        for x in self.env.cr.dictfetchall():
            ecr = x['noecr']
            lecr = x['nolecr']
            id_new = x['id_new']

            self.env.cr.execute("UPDATE compta_ligne_ecriture SET no_souscptes = %s, fg_etat= 'P' WHERE company_id = %s and x_exercice_id = %s and no_ecr = %s and no_lecr = %s" ,(id_new, v_struct, v_ex, ecr, lecr))
    



class ComptaErreurCptLine(models.Model):
    _name = "compta_erreur_cpt_line"
    
    erreur_cpt_id = fields.Many2one("compta_erreur_cpt", ondelete='cascade')
    noecr = fields.Integer("N° Ecriture" ,readonly=True)
    nolecr = fields.Integer("N° Ligne",readonly=True)
    libelle = fields.Char("Libellé",readonly=True)
    montant = fields.Integer("Montant",readonly=True)
    compte = fields.Many2one("ref_souscompte","Compte", readonly=True)
    new_compte = fields.Many2one("compta_plan_line","Nouveau Compte", required=False)
    id_new = fields.Integer()
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    
    @api.onchange("new_compte")
    def ChangeCompte(self):
        if self.new_compte:
            self.id_new = self.new_compte.souscpte.id


class ComptaAnnulerEcr(models.Model):
    _name = "compta_annuler_ecr"
    
    name = fields.Char("Nom", default="Annuler Ecriture")
    compte = fields.Many2one("compta_teneur_compte_line", required=True)
    id_compte = fields.Integer()
    teneur = fields.Many2one('compta_teneur_compte', string='Teneur de compte', domain="[('teneur','=', user_id)]", required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)
    erreur_ecr_line = fields.One2many("compta_annuler_ecr_line", "erreur_ecr_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    
    @api.onchange("compte")
    def ChangeCompte(self):
        if self.compte:
            self.id_compte = self.compte.compte.souscpte.id
    
    def chercher(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_cpte = int(self.id_compte)
        
        for vals in self:
            vals.env.cr.execute("""select distinct l.no_ecr as noecr, l.no_lecr as ligne, l.lb_lecr as libelle, l.no_souscptes as cpte,
            l.fg_sens as sens , l.mt_lecr as montant from compta_ligne_ecriture l, ref_souscompte r
            where r.id = l.no_souscptes and l.no_souscptes = %s and l.fg_etat = 'P' 
            and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""",(v_cpte, v_ex, v_struct))
            
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.erreur_ecr_line.unlink()
            for line in rows:
                result.append((0,0, {'noecr' : line['noecr'], 'nolecr': line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant'], 'compte': line['cpte']}))
            self.erreur_ecr_line = result
    
    
    def corriger(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_id = int(self.id)
        
        self.env.cr.execute("select * from compta_annuler_ecr_line where erreur_ecr_id = %d and company_id = %d and x_exercice_id = %d" %(v_id, v_struct, v_ex))
        for x in self.env.cr.dictfetchall():
            ecr = x['noecr']
            lecr = x['nolecr']
            etat = x['fg_annul']
            
            if etat == True:
            
                self.env.cr.execute("UPDATE compta_ligne_ecriture SET fg_etat = 'A' WHERE company_id = %s and x_exercice_id = %s and no_ecr = %s and no_lecr = %s" ,(v_struct, v_ex, ecr, lecr))
    

class ComptaAnnulerEcrLine(models.Model):
    _name = "compta_annuler_ecr_line"
    
    erreur_ecr_id = fields.Many2one("compta_annuler_ecr", ondelete='cascade')
    noecr = fields.Integer("N° Ecriture" ,readonly=True)
    nolecr = fields.Integer("N° Ligne",readonly=True)
    compte = fields.Many2one("ref_souscompte","Compte", readonly=True)
    sens = fields.Char("Sens",readonly=True)
    montant = fields.Integer("Montant",readonly=True)
    fg_annul = fields.Boolean("Annuler ?")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)


class ComptaAjout(models.Model):
    _name = "compta_ajout"
    
    name = fields.Char("Nom", default="Ajouter ligne")
    compte = fields.Many2one("compta_teneur_compte_line", required=True)
    id_compte = fields.Integer()
    teneur = fields.Many2one('compta_teneur_compte', string='Teneur de compte', domain="[('teneur','=', user_id)]")
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)
    ajout_line = fields.One2many("compta_ajout_line", "ajout_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
    
    @api.onchange("compte")
    def ChangeCompte(self):
        if self.compte:
            self.id_compte = self.compte.compte.souscpte.id

class ComptaAjoutLine(models.Model):
    _name = "compta_ajout_line"
    
    ajout_id = fields.Many2one("compta_ajout", ondelete='cascade')
    compte = fields.Many2one("compta_plan_line","Compte", required=True)
    sens = fields.Selection([
        ('D', 'D'),
        ('C', 'C'),
        ], string = "Sens", required=True)
    montant = fields.Integer("Montant", required=True)
    pj = fields.Many2one("ref_piece_justificatives", "PJ", required=True)
    ref_pj = fields.Char("Ref PJ")
    annee = fields.Many2one("ref_exercice",string = "Année", required=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)



class Compta_edition_compte(models.Model):
    _name='compta_edition_compte'
    _rec_name = 'compte'
    
    compte = fields.Many2one('compta_plan_line', 'Compte')
    tout_compte = fields.Boolean('Tous les comptes', default=False)
    souscpte = fields.Integer()
    etat = fields.Selection([
        ('A', 'Annulé'),
        ('F', 'Final'),
        ('I', 'Intégré'),
        ('P', 'Provisoire'),
        ('W', 'Vérifié'),
        ('V', 'Validé')], string="Etat des lignes")
    fg_sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),
        ('M', 'Indifférent')], string='Sens')
    montant = fields.Float("Montant", readonly=True)
    mnt_debit = fields.Float("Débiteur", readonly=True)
    mnt_credit = fields.Float("Créditeur", readonly=True)
    solde_etat_ids = fields.One2many('compta_solde_etat','edition_compte_id')
    editon_compte_lines = fields.One2many('compta_edition_compte_lines','edition_compte_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('compte')
    def OnchangeCompte(self):
        
        if self.compte:
            self.souscpte = self.compte.souscpte.id
    
    
    def remplir_tenue(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_cpte = int(self.souscpte)
        val_etat = str(self.etat)
        print("etat", val_etat)
        val_sens = str(self.fg_sens)
        id_tenue = self.id
        
        if self.compte:

            for vals in self:
                vals.env.cr.execute("""select distinct l.no_ecr as noecr, l.no_lecr as noligne, l.dt_ligne as dte_ligne ,l.fg_sens as sens, l.mt_lecr as mnt,l.dt_valid as valid, l.dt_verif as verif, l.fg_etat as etat 
                from compta_ligne_ecriture l, ref_souscompte r where r.id = l.souscpte and l.no_souscptes = %s and l.x_exercice_id = %s
                and l.company_id = %s """ ,(val_cpte, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.editon_compte_lines.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['noecr'], 'num_ligne' : line['noligne'], 'date_ligne': line['dte_ligne'], 'sens': line['sens'], 'montant': line['mnt'],'valid': line['valid'],'verif': line['verif'], 'etat': line['etat']}))
                self.editon_compte_lines = result
                
                
            for vals in self:
                vals.env.cr.execute("""SELECT l.fg_etat as etat,
                count(case when l.fg_sens = 'D' then l.id end) as countd,
                sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
                count(case when l.fg_sens = 'C' then l.id end) as countc,
                sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
                from ref_souscompte r, compta_ligne_ecriture l
                WHERE r.id = l.no_souscptes and l.no_souscptes = %s
                and l.x_exercice_id = %s AND l.company_id = %s group by etat""" ,(val_cpte, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.solde_etat_ids.unlink()
                for line in rows:
                    result.append((0,0, {'etat' : line['etat'],'nbre_debit' : line['countd'], 'nbre_debit' : line['countd'],'mnt_debit': line['debiteur'], 'nbre_credit' : line['countc'],  'mnt_credit': line['crediteur']}))
                self.solde_etat_ids = result
            
            self.env.cr.execute("""SELECT
            sum( case when l.sens = 'D' then l.montant end) as debiteur,
            sum( case when l.sens = 'C' then l.montant end) as crediteur
            from compta_edition_compte_lines l
            WHERE edition_compte_id = %s
            and l.x_exercice_id = %s AND l.company_id = %s """ ,(id_tenue, val_ex, val_struct,))
            mnt = self.env.cr.dictfetchall()
            self.mnt_debit = mnt and mnt[0]['debiteur']
            self.mnt_credit = mnt and mnt[0]['crediteur']
                
        if self.compte and self.etat:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as noligne, l.no_ecr as noecr, l.dt_ligne as dte_ligne ,l.fg_sens as sens, l.mt_lecr as mnt,l.dt_valid as valid,l.dt_verif as verif, l.fg_etat as etat 
                from compta_ligne_ecriture l, where r.id = l.no_souscptes and l.no_souscptes = %s and l.x_exercice_id = %s
                and l.company_id = %s and l.fg_etat = %s """ ,(val_cpte, val_ex, val_struct, val_etat))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.editon_compte_lines.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['noecr'], 'num_ligne' : line['noligne'], 'date_ligne': line['dte_ligne'], 'sens': line['sens'], 'montant': line['mnt'],'valid': line['valid'],'verif': line['verif'],'etat': line['etat']}))
                self.editon_compte_lines = result
                
            for vals in self:
                vals.env.cr.execute("""SELECT l.fg_etat as etat,
                count(case when l.fg_sens = 'D' then l.id end) as countd,
                sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
                count(case when l.fg_sens = 'C' then l.id end) as countc,
                sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
                from ref_souscompte r, compta_ligne_ecriture l
                WHERE r.id = l.no_souscptes and l.no_souscptes = %s
                and l.x_exercice_id = %s AND l.company_id = %s and l.fg_etat = %s group by etat""" ,(val_cpte, val_ex, val_struct, val_etat))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.solde_etat_ids.unlink()
                for line in rows:
                    result.append((0,0, {'etat' : line['etat'],'nbre_debit' : line['countd'], 'nbre_debit' : line['countd'],'mnt_debit': line['debiteur'], 'nbre_credit' : line['countc'],  'mnt_credit': line['crediteur']}))
                self.solde_etat_ids = result
                
            self.env.cr.execute("""SELECT
            sum( case when l.sens = 'D' then l.montant end) as debiteur,
            sum( case when l.sens = 'C' then l.montant end) as crediteur
            from compta_edition_compte_lines l
            WHERE edition_compte_id = %s
            and l.x_exercice_id = %s AND l.company_id = %s """ ,(id_tenue, val_ex, val_struct,))
            mnt = self.env.cr.dictfetchall()
            self.mnt_debit = mnt and mnt[0]['debiteur']
            self.mnt_credit = mnt and mnt[0]['crediteur']
        
        if self.tout_compte:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as noligne, l.no_ecr as noecr, l.dt_ligne as dte_ligne ,l.fg_sens as sens, l.mt_lecr as mnt,l.dt_valid as valid,l.dt_verif as verif, l.fg_etat as etat 
                from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r where c.souscpte = l.no_souscptes and r.id = c.souscpte and l.x_exercice_id = %s and l.company_id = %s order by l.no_ecr, l.no_lecr asc """ ,(val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.editon_compte_lines.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['noecr'], 'num_ligne' : line['noligne'], 'date_ligne': line['dte_ligne'], 'sens': line['sens'], 'montant': line['mnt'],'valid': line['valid'],'verif': line['verif'], 'etat': line['etat']}))
                self.editon_compte_lines = result
        
            for vals in self:
                vals.env.cr.execute("""SELECT l.fg_etat as etat,
                count(case when l.fg_sens = 'D' then l.id end) as countd,
                sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
                count(case when l.fg_sens = 'C' then l.id end) as countc,
                sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
                from ref_souscompte r,  compta_ligne_ecriture l
                WHERE r.id = l.no_souscptes 
                and l.x_exercice_id = %s AND l.company_id = %s group by etat""" ,(val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.solde_etat_ids.unlink()
                for line in rows:
                    result.append((0,0, {'etat' : line['etat'],'nbre_debit' : line['countd'], 'nbre_debit' : line['countd'],'mnt_debit': line['debiteur'], 'nbre_credit' : line['countc'],  'mnt_credit': line['crediteur']}))
                self.solde_etat_ids = result
                
            self.env.cr.execute("""SELECT
            sum( case when l.sens = 'D' then l.montant end) as debiteur,
            sum( case when l.sens = 'C' then l.montant end) as crediteur
            from compta_edition_compte_lines l
            WHERE edition_compte_id = %s
            and l.x_exercice_id = %s AND l.company_id = %s """ ,(id_tenue, val_ex, val_struct,))
            mnt = self.env.cr.dictfetchall()
            self.mnt_debit = mnt and mnt[0]['debiteur']
            self.mnt_credit = mnt and mnt[0]['crediteur']
        
        if self.tout_compte and self.etat:
            for vals in self:
                vals.env.cr.execute("""select l.no_ecr as noecr, l.no_lecr as noligne, l.dt_ligne as dte_ligne ,l.fg_sens as sens, l.mt_lecr as mnt,l.dt_valid as valid,l.dt_verif as verif, l.fg_etat as etat 
                from compta_ligne_ecriture l, compta_plan_line c where c.souscpte = l.no_souscptes and r.id = c.souscpte and l.x_exercice_id = %s
                and l.company_id = %s and l.fg_etat = %s """ ,(val_ex, val_struct, val_etat))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.editon_compte_lines.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['noecr'], 'num_ligne' : line['noligne'], 'date_ligne': line['dte_ligne'], 'sens': line['sens'], 'montant': line['mnt'],'valid': line['valid'],'verif': line['verif'],'etat': line['etat']}))
                self.editon_compte_lines = result
      

            for vals in self:
                vals.env.cr.execute("""SELECT l.fg_etat as etat,
                count(case when l.fg_sens = 'D' then l.id end) as countd,
                sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
                count(case when l.fg_sens = 'C' then l.id end) as countc,
                sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
                from ref_souscompte r,  compta_ligne_ecriture l
                WHERE r.id = l.no_souscptes and l.fg_etat = %s
                and l.x_exercice_id = %s AND l.company_id = %s group by etat""" ,(val_etat, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.solde_etat_ids.unlink()
                for line in rows:
                    result.append((0,0, {'etat' : line['etat'],'nbre_debit' : line['countd'], 'nbre_debit' : line['countd'],'mnt_debit': line['debiteur'], 'nbre_credit' : line['countc'],  'mnt_credit': line['crediteur']}))
                self.solde_etat_ids = result
                
            self.env.cr.execute("""SELECT
            sum( case when l.sens = 'D' then l.montant end) as debiteur,
            sum( case when l.sens = 'C' then l.montant end) as crediteur
            from compta_edition_compte_lines l
            WHERE edition_compte_id = %s
            and l.x_exercice_id = %s AND l.company_id = %s """ ,(id_tenue, val_ex, val_struct,))
            mnt = self.env.cr.dictfetchall()
            self.mnt_debit = mnt and mnt[0]['debiteur']
            self.mnt_credit = mnt and mnt[0]['crediteur']
                
     
 
        self.env.cr.execute("""SELECT sum(montant)
        FROM compta_edition_compte_lines WHERE x_exercice_id = %d AND company_id = %d AND edition_compte_id = %d """ %(val_ex, val_struct, id_tenue))
        res = self.env.cr.fetchone()
        self.montant = res and res[0]
        val_mnt = self.montant

    
    
class Compta_edition_compte_lines(models.Model):
    _name='compta_edition_compte_lines'
    
    edition_compte_id = fields.Many2one('compta_edition_compte', ondelete='cascade')
    no_ecr = fields.Char("N° Ecriture", readonly=True)
    num_ligne = fields.Char(string="N° Lignes", readonly=True)
    date_ligne = fields.Char("Date", readonly=True)
    ligne = fields.Char("Libellé", readonly=True)
    sens = fields.Char("Sens", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    etat = fields.Char("Etat", readonly=True)
    verif = fields.Date("Dt Vérification", readonly=True)
    valid = fields.Date("Dt Validation", readonly=True)    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class SoldeEtat(models.Model):
    _name = "compta_solde_etat"
    
    edition_compte_id = fields.Many2one('compta_edition_compte', ondelete='cascade')
    etat = fields.Char("Etat", readonly=True)
    nbre_credit = fields.Integer("Nbre Crédit", readonly=True)
    mnt_credit = fields.Float("Crébit", readonly=True)
    nbre_debit = fields.Integer("Nbre Débit", readonly=True)
    mnt_debit = fields.Float("Débit", readonly=True)
   

class Compta_dev_solde(models.Model):
    _name='compta_dev_solde'
    _rec_name='compte'
    
    compte = fields.Selection([
        ('CA', "Comptes d'attente"),
        ('CF', "Comptes financiers")
        ],"Compte")
    dt_maxi = fields.Date("Date maximum", default=fields.Date.context_today)
    dev_lines = fields.One2many("compta_dev_solde_lines", 'dev_id', readonl=True)
    state = fields.Selection([
        ('N', 'Nouveau'),
        ('T','Terminé')
        ], "Etat",default="N")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    def remplir_solde(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_dte = str(self.dt_maxi)

        if self.compte == "CA":
            for vals in self:
                vals.env.cr.execute("""select r.souscpte as compte, r.lb_long as libelle,l.fg_sens as sens , 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as p,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as r,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as vw, 
                    sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
                    sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c ,ref_souscompte r where c.souscpte = r.id and l.no_souscptes = r.id and l.dt_ligne <= %s
                    and c.fg_attente = True and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('P', 'W', 'R', 'V') 
                    group by r.souscpte , l.fg_sens , r.lb_long """ ,(val_dte, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.dev_lines.unlink()
                for line in rows:
                    result.append((0,0, {'cpte' : line['compte'], 'fg_sens': line['sens'], 'libelle': line['libelle'], 'verifvalid': line['vw'], 'rejet': line['r'], 'provisoire': line['p'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                self.dev_lines = result
        else:
            for vals in self:
                vals.env.cr.execute("""select r.souscpte as compte, r.lb_long as libelle,l.fg_sens as sens , 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as p,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as r,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as vw, 
                    sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
                    sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c ,ref_souscompte r where c.souscpte = r.id and l.no_souscptes = r.id and l.dt_ligne <= %s
                    and c.fg_finance = True and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('P', 'W', 'R', 'V') 
                    group by r.souscpte , l.fg_sens , r.lb_long """ ,( val_dte, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.dev_lines.unlink()
                for line in rows:
                    result.append((0,0, {'cpte' : line['compte'], 'fg_sens': line['sens'], 'libelle': line['libelle'], 'verifvalid': line['vw'], 'rejet': line['r'], 'provisoire': line['p'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                self.dev_lines = result
                
        self.write({'state': 'T'})
        
    @api.onchange('dt_maxi')
    def date_maxi(self):
        val_date = date.today()
        
        if self.dt_maxi > val_date:
            raise ValidationError(_("La date maximale ne peut pas être supérieure à la date du jour"))


class Compta_dev_solde_lines(models.Model):
    _name='compta_dev_solde_lines'
    
    dev_id = fields.Many2one("compta_dev_solde", ondelete='cascade')
    cpte = fields.Char("Compte")
    souscpte = fields.Char("Sous compte")
    libelle = fields.Char("Intitulé")
    verifvalid = fields.Char("#VW")
    provisoire = fields.Char("#P")
    rejet = fields.Char("#R")
    debit = fields.Integer("Total débit")
    credit = fields.Integer("Total crédit")
    fg_sens = fields.Char("Sens")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    

class ComptaDevSoldeDetail(models.Model):
    _name = 'compta_dev_solde_detail'
    
    name = fields.Char("Name", default="Développement de solde détaillé")
    compte = fields.Selection([
        ('CA', "Comptes d'attente"),
        ('CF', "Comptes financiers")
        ],"Compte", default="CA")
    cpte_financier = fields.Many2one("compta_plan_line", string="Comptes financiers", domain = [('fg_finance', '=', True)])
    c_f = fields.Integer()
    cpte_attente = fields.Many2one("compta_plan_line", string="Comptes d'attentes", domain = [('fg_attente', '=', True)])
    c_a = fields.Integer()
    credit = fields.Float("Crédit",readonly=True)
    debit = fields.Float("Débit",readonly=True)
    solde = fields.Float("Solde",readonly=True)
    etat_solde = fields.Char("", readonly=True)
    dte = fields.Date("Date maximum", default=fields.Date.context_today)
    dev_det_lines = fields.One2many("compta_dev_solde_detail_line", 'dev_det_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('cpte_financier')
    def cf(self):
        if self.cpte_financier:
            self.c_f = self.cpte_financier.souscpte.id
    
    @api.onchange('cpte_attente')
    def ca(self):
        if self.cpte_attente:
            self.c_a = self.cpte_attente.souscpte.id
    
    
    def afficher(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_cpte = int(self.c_a)
        v_cpt = int(self.c_f)
        v_dte = self.dte
        v_id = int(self.id)
        
             
        if self.compte == 'CA':
            for vals in self:
                vals.env.cr.execute("""select no_lecr as nolecr, mt_lecr as mt, fg_sens as sens, fg_etat as etat, dt_ligne as dte
                from compta_ligne_ecriture l, ref_souscompte r where l.no_souscptes = r.id and l.dt_ligne <= %s
                and r.id = %s and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('W', 'V')""" ,(v_dte, v_cpte, v_ex, v_struct))
                
                rows = vals.env.cr.dictfetchall()
                result = []
                    
                vals.dev_det_lines.unlink()
                for line in rows:
                    result.append((0,0, {'nolecr' : line['nolecr'], 'dte': line['dte'], 'mnt': line['mt'], 'sens': line['sens'], 'etat': line['etat']}))
                self.dev_det_lines = result
        
        elif self.compte == 'CF':
            for vals in self:
                vals.env.cr.execute("""select no_lecr as nolecr, mt_lecr as mt, fg_sens as sens, fg_etat as etat, dt_ligne as dte
                from compta_ligne_ecriture l, ref_souscompte r where l.no_souscptes = r.id and l.dt_ligne <= %s
                and r.id = %s and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('W', 'V')""" ,(v_dte, v_cpt, v_ex, v_struct))
                
                rows = vals.env.cr.dictfetchall()
                result = []
                    
                vals.dev_det_lines.unlink()
                for line in rows:
                    result.append((0,0, {'nolecr' : line['nolecr'], 'dte': line['dte'], 'mnt': line['mt'], 'sens': line['sens'], 'etat': line['etat']}))
                self.dev_det_lines = result
        
        
        self.env.cr.execute("""select
        sum( case when l.sens = 'D' then l.mnt end) as debiteur,
        sum( case when l.sens = 'C' then l.mnt end) as crediteur
        from compta_dev_solde_detail_line l where l.dev_det_id = %s and l.x_exercice_id = %s and l.company_id = %s""" ,(v_id, v_ex, v_struct))
        res = self.env.cr.dictfetchall()
        self.debit = res and res[0]['debiteur']
        self.credit = res and res[0]['crediteur']
        
        if self.debit > self.credit:
            self.etat_solde = "D"
        else:
            self.etat_solde = "C"
                 


class ComptaDevSoldeDetailLine(models.Model):
    _name = 'compta_dev_solde_detail_line'
    
    dev_det_id = fields.Many2one("compta_dev_solde_detail")
    nolecr = fields.Integer("N° Ligne")
    dte = fields.Date("Date")
    etat = fields.Char("Etat")
    mnt = fields.Float("Montant")
    sens = fields.Char("Sens")
    origine = fields.Char("Origine")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
  


class Compta_verif_ligne(models.Model):
    _name = 'compta_verif_ligne'
    _rec_name = 'cpte'
    
    cpte = fields.Many2one("compta_teneur_compte_line", 'Compte')
    fg_sens = fields.Char("Sens", readonly=True)
    noecr = fields.Integer("N° Ecriture")
    nolecr = fields.Integer("N° Ligne")
    date_ecr = fields.Date('Date')
    teneur = fields.Many2one("compta_teneur_compte", "Teneur de compte", required=True, domain="[('teneur','=',user_id)]")
    verif_ligne_line = fields.One2many('compta_verif_ligne_line', 'verif_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)
    
    
    def valider(self):
        
        val_cpte = int(self.cpte.compte.souscpte.id)
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_date = date.today()
        v_id = int(self.id)
        
        self.env.cr.execute("SELECT noecr, etat from compta_verif_ligne_line WHERE company_id = %s and x_exercice_id = %s and verif_id = %s" ,(val_struct, val_ex, v_id))
        
        for record in self.env.cr.dictfetchall():
            ecr = record['noecr']
            etat = record['etat']
            if etat == 'V':
                self.env.cr.execute("UPDATE compta_ecriture SET state = 'V', dt_verif = %s WHERE no_ecr = %s and company_id = %s and x_exercice_id = %s" ,(v_date,ecr,val_struct,val_ex))
                self.env.cr.execute("UPDATE compta_ligne_ecriture SET fg_etat = 'V', dt_verif = %s WHERE no_souscptes = %s and company_id = %s and x_exercice_id = %s" ,(v_date,val_cpte,val_struct,val_ex))
            elif etat == 'R':
                self.env.cr.execute("UPDATE compta_ecriture SET state = 'R', dt_verif = %s WHERE no_ecr = %s and company_id = %s and x_exercice_id = %s" ,(v_date,ecr,val_struct,val_ex))
                self.env.cr.execute("UPDATE compta_ligne_ecriture SET fg_etat = 'R', dt_verif = %s WHERE no_souscptes = %s and company_id = %s and x_exercice_id = %s" ,(v_date, val_cpte,val_struct,val_ex))


    def chercher_ligne(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_cpte = int(self.cpte.compte.souscpte.id)
        val_ecr = int(self.noecr)
        val_lecr = int(self.nolecr)
        val_dte = self.date_ecr
        

        if self.cpte:

            for vals in self:
                vals.env.cr.execute("""select DISTINCT(l.no_ecr) as noecr, l.no_lecr as ligne, concat(r.souscpte,' ', r.lb_long) as libelle, 
                l.fg_sens as sens , l.mt_lecr as montant,l.ref_pj as refp,
                l.fg_etat as etat from compta_ligne_ecriture l,compta_plan_line c, ref_souscompte r
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and l.no_souscptes = %s and l.fg_etat = 'P' 
                and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""" ,(val_cpte, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.verif_ligne_line.unlink()
                for line in rows:
                    result.append((0,0, {'noecr' : line['noecr'],'nolecr' : line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant'], 'type_pj': line['refp']}))
                self.verif_ligne_line = result
        
        elif self.noecr:
            
            for vals in self:
                vals.env.cr.execute("""select DISTINCT(l.no_ecr) as noecr, l.no_lecr as ligne, concat(r.souscpte,' ', r.lb_long) as libelle, 
                l.fg_sens as sens , l.mt_lecr as montant,l.ref_pj as refp,
                l.fg_etat as etat from compta_ligne_ecriture l,compta_plan_line c, ref_souscompte r
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and l.no_ecr = %s and l.fg_etat = 'P' 
                and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""" ,(val_ecr, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.verif_ligne_line.unlink()
                for line in rows:
                    result.append((0,0, {'noecr' : line['noecr'],'nolecr' : line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant'], 'type_pj': line['refp']}))
                self.verif_ligne_line = result
                
        elif self.nolecr:
            for vals in self:
                vals.env.cr.execute("""select DISTINCT(l.no_ecr) as noecr, l.no_lecr as ligne, concat(r.souscpte,' ', r.lb_long) as libelle, 
                l.fg_sens as sens , l.mt_lecr as montant,l.ref_pj as refp,
                l.fg_etat as etat from compta_ligne_ecriture l,compta_plan_line c, ref_souscompte r
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and l.no_lecr = %s and l.fg_etat = 'P' 
                and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""" ,(val_lecr, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.verif_ligne_line.unlink()
                for line in rows:
                    result.append((0,0, {'noecr' : line['noecr'],'nolecr' : line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant'], 'type_pj': line['refp']}))
                self.verif_ligne_line = result
        
        elif self.date_ecr:
            for vals in self:
                vals.env.cr.execute("""select DISTINCT(l.no_ecr) as noecr, l.no_lecr as ligne, concat(r.souscpte,' ', r.lb_long) as libelle, 
                l.fg_sens as sens , l.mt_lecr as montant,l.ref_pj as refp,
                l.fg_etat as etat from compta_ligne_ecriture l,compta_plan_line c, ref_souscompte r
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and l.dt_ligne = %s and l.fg_etat = 'P' 
                and l.x_exercice_id = %s and l.company_id = %s order by ligne asc""" ,(val_dte, val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.verif_ligne_line.unlink()
                for line in rows:
                    result.append((0,0, {'noecr' : line['noecr'],'nolecr' : line['ligne'], 'libelle': line['libelle'], 'sens': line['sens'], 'montant': line['montant'], 'type_pj': line['refp']}))
                self.verif_ligne_line = result
            
    
    """
    @api.onchange('user_id')
    def Est_teneur(self):
        cd_user = int(self.user_id)
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
       
        self.env.cr.execute("SELECT user_id FROM compta_teneur_cpte whereuser_id = %d AND x_exercice_id = %d AND company_id = %d" %(cd_user, val_ex, val_struct))
        curs = self.env.cr.fetchone()
        cursor_teneur = curs and curs[0] or 0       
        print('le teneur de compte est',cursor_teneur)
        
        if self.user_id != cursor_teneur:
            raise ValidationError(_("Vous n'êtes pas teneur de compte"))
    """
            
class Compta_verif_ligne_line(models.Model):
    _name='compta_verif_ligne_line'
    
    verif_id = fields.Many2one('compta_verif_ligne', ondelete='cascade')
    noecr = fields.Char("N° Ecriture", readonly=True)
    nolecr = fields.Char("N° Ligne", readonly=True)
    libelle = fields.Char("Libellé", readonly=True)
    sens = fields.Char("Sens", readonly=True)
    montant = fields.Integer("Montant", readonly=True)
    type_pj = fields.Char("Type PJ", readonly=True)
    etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Vérifié'),
        ('R', 'Rejet')
        ], string='Etat', default= "P")
    motif_rejet = fields.Text('Motif rejet')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_edition_ecriture(models.TransientModel):
    _name='compta_edition_ecriture'
    _rec_name = ''
    
    name = fields.Char("nom", default="Visu/Edition Ecriture")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture')
    etat_ecriture = fields.Boolean('Toutes les ecritures')
    no_lecr = fields.Integer('N° Ligne')
    ecr = fields.Integer('N° Ecriture')
    egalite_ecr = fields.Selection([
        ('<', 'Inférieur à'),
        ('=', 'Egal à'),
        ('>', 'Supérieur à'),
        ], 'Etat')
    type_journal = fields.Many2one("compta_type_journal")
    date_ecr = fields.Date('Date')
    egalite_date = fields.Selection([
        ('<', 'Inférieur à'),
        ('=', 'Egal à'),
        ('>', 'Supérieur à'),
        ], 'Etat date')
    createur = fields.Char('Créateur')
    edition_ecriture_line = fields.One2many('compta_edition_ecriture_line', 'edition_ecriture_id', readonly=True)
    
    
    def chercher_ecriture(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_dt = self.date_ecr
        val_lecr = int(self.no_lecr)
        val_ecr = int(self.ecr)
        val_etat = self.etat_ecriture
        val_type = int(self.type_ecriture)

        
        
        
        if self.date_ecr and self.egalite_date == '=':
            for vals in self:
                vals.env.cr.execute("""select l.no_lecr as ligne, concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens, l.mt_lecr as mnt,l.fg_etat as etat, l.type_pj as piece
                from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and l.fg_etat in ('W','V','P','R') 
                and l.dt_ligne = %s and l.company_id = %s and l.x_exercice_id = %s
                group by r.souscpte, r.lb_long, sens, ligne, mnt, etat, type_pj order by ligne asc""" ,(val_dt, val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.edition_ecriture_line.unlink()
                for line in rows:
                    result.append((0,0, {'noligne' : line['ligne'], 'cpte': line['libelle'], 'fg_sens': line['sens'], 'montant': line['mnt'], 'etat': line['etat'], 'type_pj': line['piece']}))
                self.edition_ecriture_line = result
        elif self.date_ecr and self.date_ecr == '<':
            for vals in self:
                vals.env.cr.execute("""select l.no_lecr as ligne, concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens, l.mt_lecr as mnt,l.fg_etat as etat, l.type_pj as piece
                from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and l.fg_etat in ('W','V','P','R') 
                and l.dt_ligne < %s and l.company_id = %s and l.x_exercice_id = %s
                group by libelle, sens, ligne, mnt, etat, type_pj order by ligne asc""" ,(val_dt, val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.edition_ecriture_line.unlink()
                for line in rows:
                    result.append((0,0, {'noligne' : line['ligne'], 'cpte': line['libelle'], 'fg_sens': line['sens'], 'montant': line['mnt'], 'etat': line['etat'], 'type_pj': line['piece']}))
                self.edition_ecriture_line = result
        elif self.date_ecr and self.date_ecr == '>':
            for vals in self:
                vals.env.cr.execute("""select l.no_lecr as ligne, concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens, l.mt_lecr as mnt,l.fg_etat as etat, l.type_pj as piece
                from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and l.fg_etat in ('W','V','P','R') 
                and l.dt_ligne > %s and l.company_id = %s and l.x_exercice_id = %s
                group by libelle, sens, ligne, mnt, etat, type_pj order by libelle asc""" ,(val_dt, val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.edition_ecriture_line.unlink()
                for line in rows:
                    result.append((0,0, {'noligne' : line['ligne'], 'cpte': line['libelle'], 'fg_sens': line['sens'], 'montant': line['mnt'], 'etat': line['etat'], 'type_pj': line['piece']}))
                self.edition_ecriture_line = result
               
        if self.etat_ecriture == True:
            for vals in self:
                vals.env.cr.execute("""select l.no_lecr as ligne, concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens, l.mt_lecr as mnt, l.fg_etat as etat, l.type_pj as piece
                from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r, compta_ecriture e
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes 
                and l.company_id = %s and l.x_exercice_id = %s
                group by r.souscpte, r.lb_long, sens, ligne, mnt, etat, type_pj order by ligne, libelle asc""" ,(val_struct,val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.edition_ecriture_line.unlink()
                for line in rows:
                    result.append((0,0, {'noligne' : line['ligne'], 'cpte': line['libelle'], 'fg_sens': line['sens'], 'montant': line['mnt'],  'etat': line['etat'], 'type_pj': line['piece']}))
                self.edition_ecriture_line = result
        
        if self.type_ecriture:
            for vals in self:
                vals.env.cr.execute("""select l.no_lecr as ligne, concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens, l.mt_lecr as mnt, l.fg_etat as etat, l.type_pj as piece
                from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r, compta_ecriture e
                where c.souscpte = l.no_souscptes and r.id = l.no_souscptes and e.type_ecriture = %s
                and l.company_id = %s and l.x_exercice_id = %s
                group by r.souscpte, r.lb_long, sens, ligne, mnt, etat, type_pj order by ligne, libelle asc""" ,(val_type, val_struct,val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.edition_ecriture_line.unlink()
                for line in rows:
                    result.append((0,0, {'noligne' : line['ligne'], 'cpte': line['libelle'], 'fg_sens': line['sens'], 'montant': line['mnt'], 'etat': line['etat'], 'type_pj': line['piece']}))
                self.edition_ecriture_line = result
        
        
        
        if self.no_lecr:
            for vals in self:
                vals.env.cr.execute("""select l.no_lecr as ligne, concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens, l.mt_lecr as mnt, l.fg_etat as etat, l.type_pj as piece
                from compta_ligne_ecriture l,compta_plan_line c,  ref_souscompte r where r.id = l.no_souscptes and c.souscpte = l.no_souscptes and
                l.fg_etat in ('W','V','P','R') and l.no_lecr = %s and l.company_id = %s and l.x_exercice_id = %s
                group by r.souscpte, r.lb_long, sens, ligne, mnt, etat, type_pj order by libelle asc""" ,(val_lecr, val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.edition_ecriture_line.unlink()
                for line in rows:
                    result.append((0,0, {'noligne' : line['ligne'], 'cpte': line['libelle'], 'fg_sens': line['sens'], 'montant': line['mnt'], 'etat': line['etat'], 'type_pj': line['piece']}))
                self.edition_ecriture_line = result
                
        if self.ecr:
            for vals in self:
                vals.env.cr.execute("""select l.no_lecr as ligne, concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens, l.mt_lecr as mnt, l.fg_etat as etat, l.type_pj as piece
                from compta_ligne_ecriture l,compta_plan_line c, ref_souscompte r
                where r.id = l.no_souscptes and c.souscpte = l.no_souscptes and l.fg_etat in ('W','V','P','R') and l.no_ecr = %s
                and l.company_id = %s and l.x_exercice_id = %s group by r.souscpte, r.lb_long, sens, ligne, mnt, etat, type_pj order by libelle asc""" ,(val_ecr, val_struct, val_ex))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.edition_ecriture_line.unlink()
                for line in rows:
                    result.append((0,0, {'noligne' : line['ligne'], 'cpte': line['libelle'], 'fg_sens': line['sens'], 'montant': line['mnt'], 'type_pj': line['piece'], 'etat': line['etat'], 'type_pj': line['piece']}))
                self.edition_ecriture_line = result        
                
        
class Compta_edition_ecriture_line(models.TransientModel):
    _name='compta_edition_ecriture_line'
    
    edition_ecriture_id = fields.Many2one('compta_edition_ecriture', ondelete = 'cascade')
    noligne = fields.Integer('N° Lignes')
    cpte = fields.Char('Compte')
    type_pj = fields.Many2one("compta_piece_line",'Type PJ')
    fg_sens = fields.Char('Sens')
    montant = fields.Integer('Montant')
    etat = fields.Char('Etat')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_controle_compte(models.Model):
    _name='compta_controle_compte'
    _rec_name='type_periode'
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    type_periode = fields.Selection([
        ('D', 'Décade'),
        ('E', "Exercice (hors balance d'entrée) "),
        ], 'Période')
    periode = fields.Many2one("compta_periode","Intitulé")
    periode_deb = fields.Date()
    periode_fin = fields.Date()
    etat_ligne = fields.Selection([
        ('T', 'Toutes les lignes'),
        ('NV', 'Non vérifiées'),
        ('NR', 'Non régularisées'),
        ], required=True)
    controle_compte_ligne = fields.One2many('compta_controle_compte_ligne', 'controle_compte_id')

    
    @api.onchange('periode')
    def Periode(self):

        if self.periode:
            self.periode_deb = self.periode.dt_debut
            self.periode_fin = self.periode.dt_fin
    
    def chercher_compte(self):
        
        val_ex = int(self.x_exercice_id.id)
        val_struct = int(self.company_id.id)
        val_deb = str(self.periode_deb)
        val_fin = str(self.periode_fin)
        
        if self.type_periode == 'D':
            if self.etat_ligne == 'T':
                for vals in self:
                    vals.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as libelle,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as valide, 
                    count( case when l.fg_etat = 'V' then l.fg_etat end) as verifie, 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as provisoire,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as rejet,
                    coalesce(sum( case when l.fg_sens = 'D' then l.mt_lecr end),0) as debiteur,
                    coalesce(sum( case when l.fg_sens = 'C' then l.mt_lecr end),0) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                    where c.souscpte = r.id and r.id = l.no_souscptes
                    and l.dt_ligne between %s and %s and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('P', 'W', 'R', 'V') 
                    group by  r.souscpte, r.lb_long order by libelle asc""",(val_deb, val_fin, val_ex, val_struct))
                    rows = vals.env.cr.dictfetchall()
                    result = []
                    
                    vals.controle_compte_ligne.unlink()
                    for line in rows:
                        result.append((0,0, {'cpte' : line['libelle'], 'valide': line['valide'], 'verifie': line['verifie'], 'provisoire': line['provisoire'], 'rejet': line['rejet'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                    self.controle_compte_ligne = result
            elif self.etat_ligne == 'NV':
                for vals in self:
                    vals.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as libelle,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as valide, 
                    count( case when l.fg_etat = 'V' then l.fg_etat end) as verifie, 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as provisoire,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as rejet,
                    coalesce(sum( case when l.fg_sens = 'D' then l.mt_lecr end),0) as debiteur,
                    coalesce(sum( case when l.fg_sens = 'C' then l.mt_lecr end),0) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                    where c.souscpte = r.id and r.id = l.no_souscptes 
                    and l.dt_ligne between %s and %s and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('P','R') 
                    group by  r.souscpte, r.lb_long order by libelle asc""",(val_deb, val_fin, val_ex, val_struct))
                    rows = vals.env.cr.dictfetchall()
                    result = []
                    
                    vals.controle_compte_ligne.unlink()
                    for line in rows:
                        result.append((0,0, {'cpte' : line['libelle'], 'valide': line['valide'], 'verifie': line['verifie'], 'provisoire': line['provisoire'], 'rejet': line['rejet'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                    self.controle_compte_ligne = result
            elif self.etat_ligne == 'NR':
                for vals in self:
                    vals.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as libelle,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as valide, 
                    count( case when l.fg_etat = 'V' then l.fg_etat end) as verifie, 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as provisoire,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as rejet,
                    sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
                    sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                    where c.souscpte = r.id and r.id = l.no_souscptes 
                    and l.fg_sens = 'M' and l.dt_ligne between %s and %s and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('P', 'W', 'R', 'V') 
                    group by  r.souscpte, r.lb_long order by libelle asc""",(val_deb, val_fin, val_ex, val_struct))
                    rows = vals.env.cr.dictfetchall()
                    result = []
                    
                    vals.controle_compte_ligne.unlink()
                    for line in rows:
                        result.append((0,0, {'cpte' : line['libelle'], 'valide': line['valide'], 'verifie': line['verifie'], 'provisoire': line['provisoire'], 'rejet': line['rejet'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                    self.controle_compte_ligne = result
        elif self.type_periode == 'E':
            if self.etat_ligne == 'T':
                for vals in self:
                    vals.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as libelle,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as valide, 
                    count( case when l.fg_etat = 'V' then l.fg_etat end) as verifie, 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as provisoire,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as rejet,
                    coalesce(sum( case when l.fg_sens = 'D' then l.mt_lecr end),0) as debiteur,
                    coalesce(sum( case when l.fg_sens = 'C' then l.mt_lecr end),0) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                    where c.souscpte = r.id and r.id = l.no_souscptes
                    and l.x_exercice_id = %s and l.company_id = %s and l.no_ecr > 0 and l.fg_etat in ('P', 'W', 'R', 'V') 
                    group by  r.souscpte, r.lb_long order by libelle asc """,(val_ex, val_struct))
                    rows = vals.env.cr.dictfetchall()
                    result = []
                    
                    vals.controle_compte_ligne.unlink()
                    for line in rows:
                        result.append((0,0, {'cpte' : line['libelle'], 'valide': line['valide'], 'verifie': line['verifie'], 'provisoire': line['provisoire'], 'rejet': line['rejet'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                    self.controle_compte_ligne = result
            elif self.etat_ligne == 'NV':
                for vals in self:
                    vals.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as libelle,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as valide, 
                    count( case when l.fg_etat = 'V' then l.fg_etat end) as verifie, 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as provisoire,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as rejet,
                    coalesce(sum( case when l.fg_sens = 'D' then l.mt_lecr end),0) as debiteur,
                    coalesce(sum( case when l.fg_sens = 'C' then l.mt_lecr end),0) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                    where c.souscpte = r.id and r.id = l.no_souscptes
                    and l.no_ecr > 0 and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('P','R') 
                    group by  r.souscpte, r.lb_long order by libelle asc """,(val_ex, val_struct))
                    rows = vals.env.cr.dictfetchall()
                    result = []
                    
                    vals.controle_compte_ligne.unlink()
                    for line in rows:
                        result.append((0,0, {'cpte' : line['libelle'], 'valide': line['valide'], 'verifie': line['verifie'], 'provisoire': line['provisoire'], 'rejet': line['rejet'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                    self.controle_compte_ligne = result
            elif self.etat_ligne == 'NR':
                for vals in self:
                    vals.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as libelle,
                    count( case when l.fg_etat = 'W' then l.fg_etat end) as valide, 
                    count( case when l.fg_etat = 'V' then l.fg_etat end) as verifie, 
                    count( case when l.fg_etat = 'P' then l.fg_etat end) as provisoire,
                    count( case when l.fg_etat = 'R' then l.fg_etat end) as rejet,
                    coalesce(sum( case when l.fg_sens = 'D' then l.mt_lecr end),0) as debiteur,
                    coalesce(sum( case when l.fg_sens = 'C' then l.mt_lecr end),0) as crediteur
                    from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r
                    where c.souscpte = r.id and r.id = l.no_souscptes
                    and l.fg_sens = 'M' and l.no_ecr > 0 and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat in ('P', 'W', 'R', 'V') 
                    group by  r.souscpte, r.lb_long order by libelle asc """,(val_ex, val_struct))
                    rows = vals.env.cr.dictfetchall()
                    result = []
                    
                    vals.controle_compte_ligne.unlink()
                    for line in rows:
                        result.append((0,0, {'cpte' : line['libelle'], 'valide': line['valide'], 'verifie': line['verifie'], 'provisoire': line['provisoire'], 'rejet': line['rejet'], 'debit': line['debiteur'], 'credit': line['crediteur']}))
                    self.controle_compte_ligne = result
            
        

class Compta_controle_compte_ligne(models.Model):
    _name='compta_controle_compte_ligne'
    
    controle_compte_id = fields.Many2one('compta_controle_compte', ondelete='cascade')
    cpte = fields.Char("N° et intitulé du compte")
    valide = fields.Integer("#W")
    verifie = fields.Integer("#V")
    provisoire = fields.Integer("#P")
    rejet = fields.Integer("#R")
    debit = fields.Integer("Total débit")
    credit = fields.Integer("Total crédit")
    teneur = fields.Char("Teneur du compte")
    
    
    
class Compta_ecriture_deseq(models.Model):
    _name='compta_ecriture_deseq'
    _rec_name = 'x_exercice_id'
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    ecriture_deseq_line = fields.One2many("compta_ecriture_deseq_line", 'ecriture_deseq_id')
    
    def chercher_ecriture(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
    
    
        for vals in self:
            vals.env.cr.execute("""select l.no_ecr as ecr, dt_ligne as dte,
            sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
            sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
            from compta_ligne_ecriture l where l.x_exercice_id = %s and l.company_id = %s
            and l.fg_etat <> 'A' group by l.no_ecr, l.dt_ligne order by ecr""",(val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.ecriture_deseq_line.unlink()
            for line in rows:
                result.append((0,0, {'noecr' : line['ecr'], 'dt_ligne': line['dte'], 'mnt_debit': line['debiteur'], 'mnt_credit': line['crediteur']}))
            self.ecriture_deseq_line = result
        
        for x in self.ecriture_deseq_line:
            x.difference = x.mnt_debit - x.mnt_credit
            
            

class Compta_ecriture_deseq_line(models.Model):
    _name='compta_ecriture_deseq_line'
    
    ecriture_deseq_id = fields.Many2one("compta_ecriture_deseq", ondelete='cascade')
    noecr = fields.Integer("N° Ecriture", readonly=True)
    dt_ligne = fields.Date("Date ligne", readonly=True)
    mnt_debit = fields.Integer("Somme débit", readonly=True)
    mnt_credit = fields.Integer("Somme crédit", readonly=True)
    difference = fields.Integer("D - C", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    

class Compta_ecriture_dt(models.Model):
    _name='compta_ecriture_dt'
    _rec_name = 'x_exercice_id'
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    ecriture_dt_line = fields.One2many("compta_ecriture_dt_line", 'ecriture_deseq_id')
    
    def chercher_ecriture(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
    
        self.env.cr.execute("select distinct extract( year from dt_ligne) from compta_ligne_ecriture where company_id = %d and x_exercice_id = %d" %(val_struct, val_ex))
        res = self.env.cr.fetchone()
        dt = res and res[0] or 0
        dt = dt
        
        for vals in self:
            vals.env.cr.execute("""select distinct l.no_ecr as ecr, e.dt_ecriture as dte ,l.no_lecr as lecr, dt_ligne as dtes, l.no_souscptes as imput, l.fg_etat as etat
            from compta_ligne_ecriture l, compta_ecriture e, ref_exercice r 
            where l.x_exercice_id = %s and l.company_id = %s and r.id = l.company_id and e.no_ecr = l.no_ecr
            and r.no_ex != %s and l.fg_etat <> 'A' order by ecr""",(val_ex, val_struct,dt))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.ecriture_dt_line.unlink()
            for line in rows:
                result.append((0,0, {'noecr' : line['ecr'], 'dt_ligne': line['dte'], 'no_lecr': line['lecr'], 'dt_lignes': line['dtes'], 'imputation': line['imput'], 'etat': line['etat']}))
            self.ecriture_dt_line = result
        
            
class Compta_ecriture_dt_line(models.Model):
    _name='compta_ecriture_dt_line'
    
    ecriture_deseq_id = fields.Many2one("compta_ecriture_dt", ondelete='cascade')
    noecr = fields.Integer("N° Ecriture", readonly=True)
    dt_ligne = fields.Date("Date Ecriture", readonly=True)
    no_lecr = fields.Integer("N° Lignes", readonly=True)
    dt_lignes = fields.Date("Date lignes", readonly=True)
    imputation = fields.Many2one("ref_souscompte", "Imputation", readonly=True)
    etat = fields.Char("Etat", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


 
class Compta_tenue_compte(models.Model):
    _name="compta_tenue_compte"
    _rec_name='teneur'
    
    dt_debut = fields.Date("Date de début", required=True)
    dt_fin = fields.Date("Date de fin", default=fields.Date.context_today, required=True)
    teneur = fields.Many2one("compta_teneur_compte", "Teneur de compte", domain = " [('teneur','=',user_id)]", required=True)
    tenue_compte_line = fields.One2many("compta_tenue_compte_line", "tenue_compte_id", readonly=True)
    user_id = fields.Many2one('res.users', string = 'user', readonly = True, default = lambda self:self.env.user)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    @api.onchange('dt_debut', 'dt_fin')
    def change_date(self):
        val = date.today()
        """
        if self.dt_debut > self.dt_fin:
            raise ValidationError(_('La date de début doit être inférieure à la date de fin'))
        """
        if self.dt_fin > val:
            raise Warning(_('La date de fin doit être inférieure ou égale à la date du jour'))
        
    
    def afficher_ligne(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_user = int(self.teneur)
        val_deb = str(self.dt_debut)
        val_fin = str(self.dt_fin)

        for vals in self:
            vals.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as libelle,l.fg_sens as sens,
            count( case when l.fg_etat = 'V' then l.fg_etat end) as verifie, 
            count( case when l.fg_etat = 'P' then l.fg_etat end) as provisoire,
            count( case when l.fg_etat = 'R' then l.fg_etat end) as rejet,
            sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,
            sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur
            from compta_ligne_ecriture l, compta_plan_line c, ref_souscompte r, compta_teneur_compte t, compta_teneur_compte_line tl
            where tl.compte = c.id and tl.teneur_id = t.id and c.souscpte = l.no_souscptes and l.no_souscptes = r.id and t.id = %s and  
            l.fg_etat in ('V','P','R') and l.dt_ligne between %s and %s and l.x_exercice_id = %s
            and l.company_id = %s group by r.souscpte,  r.lb_long, l.fg_sens order by libelle asc""" ,(val_user, val_deb, val_fin, val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.tenue_compte_line.unlink()
            for line in rows:
                result.append((0,0, {'cpte' : line['libelle'], 'sens': line['sens'], 'verifie': line['verifie'], 'provisoire': line['provisoire'], 'rejet': line['rejet'], 'mnt_debit': line['debiteur'], 'mnt_credit': line['crediteur']}))
            self.tenue_compte_line = result
        

class Compta_tenue_compte_line(models.Model):
    _name='compta_tenue_compte_line'
    
    tenue_compte_id = fields.Many2one("compta_tenue_compte", ondelete='cascade')
    cpte = fields.Char("N° et intitulé du compte")
    sens = fields.Char("Sens")
    total = fields.Integer("Total")
    verifie = fields.Integer("Vérifiée")
    provisoire = fields.Integer("Provisoire")
    rejet = fields.Integer("Rejétée")
    mnt_debit = fields.Float("Montant débit")
    mnt_credit = fields.Float("Montant crédit")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_balance_generale(models.Model):
    _name='compta_balance_generale'
    
    name = fields.Char("Titre",default ="Balance générale des opérations")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    balance_generale_line = fields.One2many("compta_balance_generale_line", "balance_generale_id", readonly=True)
    
    
    def afficher_balance(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        for vals in self:
            vals.env.cr.execute(""" select l.souscpte as scpte, r.lb_long as lib from compta_plan_line l, ref_souscompte r where company_id = %d and x_exercice_id = %d and r.id = l.souscpte order by l.souscpte """ %(val_struct, val_ex))
      
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.balance_generale_line.unlink()
                        
            for line in rows:
                result.append((0,0, {'souscpte' : line['scpte'],'libelle' : line['lib']}))
            self.balance_generale_line = result
        
        self.Calcul()
        
        
    def Calcul(self):
        v_id = int(self.id)
        print("ident", v_id)
        val_ex = int(self.x_exercice_id)
        print("exerc", val_ex)
        val_struct = int(self.company_id)
        print("struct", val_struct)
        self.env.cr.execute("select souscpte from compta_balance_generale_line where balance_generale_id = %d" %(v_id))
        for vals in self.env.cr.dictfetchall():
            cptes = vals['souscpte']
            cpte = int(cptes)
            print("compte", type(cpte))
            
            self.env.cr.execute("""select concat(r.souscpte, ' ', r.lb_long) as compte, 
            coalesce(sum( case when l.fg_sens = 'D' and no_ecr = 0 then l.mt_lecr end),0) as bdebiteur,
            coalesce(sum( case when l.fg_sens = 'C' and no_ecr = 0 then l.mt_lecr end),0) as bcrediteur,
            coalesce(sum( case when l.fg_sens = 'D' and no_ecr != 0 then l.mt_lecr end),0) as mvdebiteur,
            coalesce(sum( case when l.fg_sens = 'C' and no_ecr != 0 then l.mt_lecr end),0) as mvcrediteur
            from ref_souscompte r,compta_plan_line c, compta_ligne_ecriture l where r.id = l.no_souscptes and c.souscpte = l.no_souscptes and r.id = %d
            and l.company_id = %d and l.x_exercice_id = %d and l.fg_etat != 'A' group by r.souscpte, r.lb_long order by compte asc""" %(cpte,val_struct, val_ex))
            for res in self.env.cr.dictfetchall():
                
                bdebits = res['bdebiteur']
                print("bdebit", bdebits)
                bdebit = int(bdebits)
                bcredits = res['bcrediteur']
                print("bcredit", bcredits)
                bcredit = int(bcredits)
                mvdebits = res['mvdebiteur']
                print("mvdebit", mvdebits)
                mvdebit = int(mvdebits)
                mvcredits = res['mvcrediteur']
                print("mvcredit", mvcredits)
                mvcredit = int(mvcredits)
                
                self.env.cr.execute("""UPDATE compta_balance_generale_line SET entre_debit = %d, entre_credit = %d, mvt_debit = %d, mvt_credit = %d
                where souscpte = %d and balance_generale_id = %d""" %(bdebit, bcredit, mvdebit, mvcredit, cpte, v_id))

        for x in self.balance_generale_line:
            x.tot_mvt_debit = x.entre_debit + x.mvt_debit
            x.tot_mvt_credit = x.entre_credit + x.mvt_credit
            
            if x.tot_mvt_debit - x.tot_mvt_credit >= 0:
                x.solde_debit = x.tot_mvt_debit - x.tot_mvt_credit
            elif x.tot_mvt_credit - x.tot_mvt_debit >= 0:
                x.solde_credit = x.tot_mvt_credit - x.tot_mvt_debit
        

class Compta_balance_generale_line(models.Model):
    _name="compta_balance_generale_line"
    
    balance_generale_id = fields.Many2one("compta_balance_generale", ondelete='cascade')
    #cpte = fields.Many2one("compta_plan_line","compte")
    souscpte = fields.Many2one("ref_souscompte","N° compte", readonly=True)
    libelle = fields.Char("Libellé", readonly=True)
    entre_debit = fields.Integer("Solde. Ouv Débiteurs", readonly=True)
    entre_credit = fields.Integer("Solde. Ouv Créditeurs", readonly=True)
    mvt_debit = fields.Integer("Mvt Périod. Débits", readonly=True)
    mvt_credit = fields.Integer("Mvt Périod. Crédits", readonly=True)
    tot_mvt_debit = fields.Integer("Totaux Débiteurs", readonly=True)
    tot_mvt_credit = fields.Integer("Totaux Créditeurs", readonly=True)
    solde_debit = fields.Integer("Soldes Débiteurs", readonly=True)
    solde_credit = fields.Integer("Soldes Créditeurs", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_regle_simplifie(models.Model):
    _name='compta_regle_simplifie'
    _rec_name='lb_long'

    cd_rg_unique = fields.Char("Code", required=True, size=3)
    no_imput = fields.Many2one("compta_plan_line", "Imputation", required=True)
    no_imputs = fields.Integer()
    lb_court = fields.Char("Libellé court")
    lb_long = fields.Char("Libellé long", required=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('no_imput')
    def OnchangeImput(self):
        if self.no_imput:
            self.no_imputs = self.no_imput.souscpte.id

class Compta_CG(models.Model):
    _name='compta_cg_dep'
    
    compte_gestion = fields.Selection([        
        ('D', 'Dépenses'),
        ],default="D", string='Compte de gestion')
    name = fields.Char(default="Compte de gestion des Dépenses")
    dt_deb = fields.Date('Du')
    dt_fin = fields.Date('Au')
    cg_lines = fields.One2many("compta_cg_dep_line", "cg_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
    def chercher_cgestio(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)

        for vals in self:
            vals.env.cr.execute("""select DISTINCT rt.cd_titre as tit, rs.cd_section as sec,rc.cd_chapitre as chap, 
            ra.cd_article as art, rp.cd_paragraphe as par, br.rubrique as rub,
            ld.mnt_budgetise as initial, ld.mnt_corrige as corrige,ld.mnt_mandate as prise,ld.mnt_mandate as paiement
            from budg_ligne_exe_dep ld, ref_titre rt, ref_section rs, ref_chapitre rc, ref_article ra, ref_paragraphe rp, budg_rubrique br, budg_titre bt, budg_section bs,
            budg_chapitre bc,budg_param_article ba,  budg_paragraphe bp where rt.id = bt.titre and bt.id = ld.cd_titre_id and rs.id = bs.section and bs.id = ld.cd_section_id 
            and rc.id = bc.chapitre and bc.id = ld.cd_chapitre_id and ra.id = ba.article and ba.id = ld.cd_art_id and rp.id = bp.paragraphe 
            and bp.id = ld.cd_paragraphe_id and br.id = ld.cd_rubrique_id
            and ld.x_exercice_id = %s and ld.company_id = %s order by tit,sec, chap, art, par, rub""" ,(val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.cg_lines.unlink()
            for line in rows:
                result.append((0,0, {'cd_titre_id' : line['tit'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'], 'cd_art_id': line['art'], 'cd_paragraphe_id': line['par'], 
                'cd_rubrique_id': line['rub'],'mnt_budgetise': line['initial'],'mnt_corrige': line['corrige'],'mnt_pc': line['prise'],'mnt_paye': line['paiement']}))
            self.cg_lines = result

        for record in self.cg_lines:
            if record.mnt_corrige != 0:
                record.taux = (record.mnt_paye / record.mnt_corrige) * 100
            record.rest_payer = (record.mnt_corrige - record.mnt_paye)
    



class Compta_CgLineDep(models.Model):
    _name='compta_cg_dep_line'
    
    cg_id = fields.Many2one("compta_cg_dep", ondelete='cascade')
    cd_titre_id = fields.Char(string = "Titre", readonly=True)
    cd_section_id = fields.Char(string = "Section", readonly=True)
    cd_chapitre_id = fields.Char(string = "Chapitre", readonly=True)
    cd_art_id = fields.Char(string = "Article", readonly=True)
    cd_paragraphe_id = fields.Char(string = "Paragraphe", readonly=True)
    cd_rubrique_id = fields.Char(string = "Rubrique", readonly=True)
    mnt_budgetise = fields.Float(string = "Dotation initiale", readonly=True)
    mnt_corrige = fields.Float(string = "Dotation corrigée", readonly=True)
    mnt_pc= fields.Float(string = "Prise en Charge", readonly=True)
    mnt_paye= fields.Float(string = "Paiement", readonly=True)
    taux = fields.Float(string = "Taux d'exécution", readonly=True)
    rest_payer= fields.Float(string = "Reste à payer", readonly=True)
    budg_id = fields.Integer()
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    
class Compta_CGRec(models.Model):
    _name='compta_cg_rec'
    
    
    name = fields.Char(default="Compte de gestion des Recettes")
    compte_gestion = fields.Selection([        
        ('R', 'Recettes'),
        ],defautl="R", string='Compte de gestion')
    dt_deb = fields.Date('Du')
    dt_fin = fields.Date('Au')
    cg_lines = fields.One2many("compta_cg_rec_line", "cg_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    def chercher_cgestionrec(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)

        for vals in self:
            vals.env.cr.execute("""select DISTINCT  rt.lb_long as tit, rs.cd_section as sec,rc.cd_chapitre as chap, 
            ra.cd_article as art, rp.cd_paragraphe as par, br.rubrique as rub,
            lc.mnt_budgetise as initial, lc.mnt_corrige as corrige,lc.mnt_emis as prise, lc.mnt_rec as rec
            from budg_ligne_exe_rec lc, ref_titre rt, ref_section rs, ref_chapitre rc, ref_article ra, ref_paragraphe rp, budg_rubrique br, budg_titre bt, budg_section bs,
            budg_chapitre bc, budg_param_article ba, budg_paragraphe bp where rt.id = bt.titre and bt.id = lc.cd_titre_id and rs.id = bs.section and bs.id = lc.cd_section_id and 
            rc.id = bc.chapitre and bc.id = lc.cd_chapitre_id and ra.id = ba.article and ba.id = lc.cd_art_id and rp.id = bp.paragraphe and bp.id = lc.cd_paragraphe_id and 
            br.id = lc.cd_rubrique_id and lc.x_exercice_id = %s and lc.company_id = %s order by tit, sec, chap, art, par, rub
            """ ,(val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.cg_lines.unlink()
            for line in rows:
                result.append((0,0, {'cd_titre_id' : line['tit'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'], 'cd_art_id': line['art'], 'cd_paragraphe_id': line['par'], 
                'cd_rubrique_id': line['rub'],'mnt_budgetise': line['initial'],'mnt_corrige': line['corrige'],'mnt_pc': line['prise'],'mnt_recouvrer': line['rec']}))
            self.cg_lines = result
        
        for record in self.cg_lines:
            if record.mnt_corrige != 0:
                record.taux = (record.mnt_recouvrer / record.mnt_corrige) * 100
            record.rest_recouvrer = (record.mnt_corrige - record.mnt_recouvrer)
    

class Compta_CgLineRec(models.Model):
    _name='compta_cg_rec_line'
    
    cg_id = fields.Many2one("compta_cg_rec", ondelete='cascade')
    cd_titre_id = fields.Char(string = "Titre", readonly=True)
    cd_section_id = fields.Char(string = "Section", readonly=True)
    cd_chapitre_id = fields.Char(string = "Chapitre", readonly=True)
    cd_art_id = fields.Char(string = "Article", readonly=True)
    cd_paragraphe_id = fields.Char(string = "Paragraphe", readonly=True)
    cd_rubrique_id = fields.Char(string = "Rubrique", readonly=True)
    mnt_budgetise = fields.Float(string = "Dotation initiale", readonly=True)
    mnt_corrige = fields.Float(string = "Dotation corrigée", readonly=True)
    mnt_pc= fields.Float(string = "Prise en Charge", readonly=True)
    mnt_recouvrer= fields.Float(string = "Recouvrement", readonly=True)
    taux = fields.Float(string = "Taux d'exécution", readonly=True)
    rest_recouvrer= fields.Float(string = "Reste à recouvrer", readonly=True)
    budg_id = fields.Integer()
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Compta_type_etat_financier(models.Model):
    _name='compta_type_etat_financier'
    _rec_name = 'lb_long'
    
    cd_type_financier = fields.Char("Code")
    lb_court = fields.Char("Libellé court")
    lb_long = fields.Char("Libellé long", required=True)
    active = fields.Boolean(string="Actif", default=True)
    
    
class Compta_type_colonne_etat_financier(models.Model):
    _name='compta_type_colonne_etat_financier'
    _rec_name = 'lb_long'
    
    cd_colonne_financier = fields.Char("Code")
    lb_court = fields.Char("Libellé court")
    lb_long = fields.Char("Libellé long", required=True)
    active = fields.Boolean(string="Actif", default=True)
    

class Compta_partie_etat_financier(models.Model):
    _name='compta_partie_etat_financier'
    _rec_name = 'lb_long'
    
    cd_categorie_financier = fields.Char("Code")
    lb_court = fields.Char("Libellé court")
    lb_long = fields.Char("Libellé long", required=True)
    active = fields.Boolean(string="Actif", default=True)

class Compta_rubrique_etat_financier(models.Model):
    
    @api.depends('cd_rubrique','lb_long')
    def _concatenate_rubrique(self):
        for test in self:
            test.name = str(test.cd_rubrique)+ " " +str(test.lb_long)
            
    _name='compta_rubrique_etat_financier'
    
    name = fields.Char("Rubrique", compute="_concatenate_rubrique")
    cd_rubrique = fields.Char("Code rubrique", required=True)
    lb_court = fields.Char("Libellé court", required=False)
    lb_long = fields.Char("Libellé long", required=True)
    type_etat = fields.Many2one('compta_type_etat_financier', "Type état financier", required=True)
    type_colonne = fields.Many2one('compta_type_colonne_etat_financier', "Type colonne", required=True)
    terminal = fields.Selection([
        ('Y', 'Oui'),
        ('N', 'Non'),
        ], string='Terminal ?', required=False)
    actif = fields.Selection([
        ('Y', 'Oui'),
        ('N', 'Non'),
        ], string='Actif ?', required=False)
    ordre = fields.Char("Ordre", required=True)
    formule = fields.Text('Formule')
    existe = fields.Selection([('Y','Oui'),('N','Non')], string='Formule existe', default='N', required=True)
    variable = fields.Selection([
        ('Y', 'Oui'),
        ('N', 'Non'),
        ], string='Element variable ?')
    note = fields.Char("Note")
    signe = fields.Char("Signe")
    #x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
class Compta_parametrage(models.Model):
    _name = 'compta_param_etat_financier'
    _rec_name = 'lb_long'
    
    cd_rubrique = fields.Char("Code rubrique", readonly=True)
    lb_court = fields.Char("Libellé court", required=False)
    lb_long = fields.Many2one("compta_rubrique_etat_financier", "Libellé rubrique", required=True)
    type_etat = fields.Many2one('compta_type_etat_financier', "Type état financier", required=True)
    type_colonne = fields.Many2one("compta_type_colonne_etat_financier","Type colonne", readonly=True)
    type_categorie = fields.Selection([
        ('1','Brut'),
        ('2','Amort. & Déprec.'),
        ('3','Net N'),
        ('4','Net N-1'),
        ('5','Autres'),
        ], "Catégorie colonne", required=True, default= '5')
    terminal = fields.Selection([
        ('Y', 'Oui'),
        ('N', 'Non'),
        ], string='Terminal ?', readonly=True)
    existe = fields.Selection([('Y','Oui'),('N','Non')], string="Formule existe ?",readonly=True)
    formule = fields.Char("Formule",readonly=True)
    actif = fields.Selection([
        ('Y', 'Oui'),
        ('N', 'Non'),
        ], string='Actif ?', readonly=True)
    ordr = fields.Char("Ordre", readonly=True)
    param_etat_financier_line = fields.One2many('compta_param_etat_financier_line', 'parametrage_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('lb_long')
    def OnchangeLibelle(self):
        
        if self.lb_long:
            
            self.type_colonne = self.lb_long.type_colonne
            #self.type_categorie = self.lb_long.type_categorie
            self.terminal = self.lb_long.terminal
            self.ordr = self.lb_long.ordre
            self.actif = self.lb_long.actif
            self.existe = self.lb_long.existe
            self.formule = self.lb_long.formule
            
    
    
class Compta_parametrage_line(models.Model):
    _name = 'compta_param_etat_financier_line'
    
    parametrage_id = fields.Many2one('compta_param_etat_financier', ondelete='cascade')
    cpte = fields.Many2one('ref_compte', 'Compte', required=True)
    cptes = fields.Integer()
    libelle = fields.Char("Libelle", readonly = True)
    signe = fields.Char("Signe")
    sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crébit'),
        ('M', 'Mixte'),
        ], 'Sens', readonly=True)
    present = fields.Boolean("Présent?")
    ordre = fields.Char("N° ordre")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
    @api.onchange('cpte')
    def OnchangeCpte(self):
        if self.cpte:
            #self.cptes = self.cpte.souscpte.id
            self.libelle = self.cpte.lb_long
            #self.sens = self.cpte.fg_sens
            

class ComptatEtatFinancier(models.Model):
    _name = "compta_etat_financier"
    _rec_name = "type_etat"
    
    type_etat = fields.Many2one('compta_type_etat_financier', "Type état financier", required=True)
    observation = fields.Text('Observations')
    dte = fields.Date("Date")
    etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Validé'),
        ], 'Etat')
    detail_lines = fields.One2many("compta_detail_etat_financier","etat_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
class ComptaDetailEtatFinancier(models.Model):
    _name = "compta_detail_etat_financier"
    
    etat_id = fields.Many2one("compta_etat_financier", ondelte='cascade')
    lb_long = fields.Many2one("compta_rubrique_etat_financier", "Libellé rubrique")
    signe = fields.Char("Signe")
    sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crébit'),
        ('M', 'Mixte'),
        ], 'Sens')
    etat = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crébit'),
        ('M', 'Mixte'),
        ], 'Etat')
    cpte = fields.Many2one('compta_plan_line', 'Origine comptable')
    mnt_detail = fields.Float("Montant")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptatVisuEtatFinancier(models.Model):
    _name = "compta_visu_etat_financier"
    _rec_name = "type_etat"
    
    type_etat = fields.Many2one('compta_type_etat_financier', "Type état financier", required=True)
    observation = fields.Text('Observations')
    dte = fields.Date("Date")
    etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Validé'),
        ], 'Etat')
    detail_lines = fields.One2many("compta_detail_visu_etat_financier","etat_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
class ComptaDetailVisuEtatFinancier(models.Model):
    _name = "compta_detail_visu_etat_financier"
    
    etat_id = fields.Many2one("compta_visu_etat_financier", ondelte='cascade')
    lb_long = fields.Many2one("compta_rubrique_etat_financier", "Libellé rubrique")
    mnt_detail = fields.Float("Montant")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
class ComptaEtatFin(models.Model):
    _name = 'compta_etat_fin'
    _rec_name = "type_etat"
    
    type_etat = fields.Selection([
        ('BL', 'Bilan'),
        ('CR', 'Compte de Resultat'),
        ("AU", 'Autres')
        ], "Etat fiancier", required = True)
    dte = fields.Date("Date")
    etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Validé'),
        ], 'Etat')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    detail_ids = fields.One2many("compta_detail_etat_fin_cr", "etat_id")
    det_bla = fields.One2many("compta_detail_etat_fin_bla", "etat_id")
    det_blp = fields.One2many("compta_detail_etat_fin_blp", "etat_id")

class ComptaDetailEtatFinCr(models.Model):
    _name = 'compta_detail_etat_fin_cr'
    
    etat_id = fields.Many2one("compta_etat_fin")
    cr_ref = fields.Char("Ref")
    cr_libelle = fields.Char("Libellé")
    cr_note = fields.Char("Note")
    cr_annee_n = fields.Float("Exercice Au 31/12/N (NET)")
    cr_annee_n1 = fields.Float("Exercice Au 31/12/N-1 (NET)")

class ComptaDetailEtatFinBlA(models.Model):
    _name = 'compta_detail_etat_fin_bla'

    etat_id = fields.Many2one("compta_etat_fin")
    bl_refa = fields.Char("Ref")
    bl_actif = fields.Char("Actif")
    bl_notea = fields.Char("Note")
    bl_annee_n_brut = fields.Float("Brut")
    bl_annee_n_amort = fields.Float("Amort")
    bl_annee_n_net = fields.Float("Net")
    bl_annee_n1 = fields.Float("Exercice Au 31/12/N-1(NET)")

class ComptaDetailEtatFinBlP(models.Model):
    _name = 'compta_detail_etat_fin_blp'
    
    etat_id = fields.Many2one("compta_etat_fin")
    bl_refp = fields.Char("Ref")
    bl_passif = fields.Char("Passif")
    bl_notep = fields.Char("Note")
    bl_anneep_n = fields.Float("Exercice Au 31/12/N (NET)")
    bl_anneep_n1 = fields.Float("Exercice Au 31/12/N - 1")
    


class Compta_situation_benef(models.Model):
    _name='compta_situation_benef'
    
    benef = fields.Selection([
        ('1','Par bénéficiaire'),
        ('2','Global'),
        ],'Recherche')
    type_beneficiaire = fields.Many2one('ref_typebeneficiaire', 'Catégorie de bénéficiaire')
    nom_benef = fields.Many2one('ref_beneficiaire', 'Bénéficiaire')
    periode_deb = fields.Date('Du')
    periode_fin = fields.Date('Au')
    cd_titre_id = fields.Many2one("budg_titre",'Titre')
    cd_section_id = fields.Many2one("budg_section", "Section")
    cd_chapitre_id = fields.Many2one("budg_chapitre", "Chapitre")
    cd_article_id = fields.Many2one("budg_param_article", "Article")
    cd_paragraphe_id = fields.Many2one("budg_paragraphe", "Paragraphe")
    cd_rubrique_id = fields.Many2one("budg_rubrique", "Rubrique")
    etat = fields.Selection([
        ('E', 'Ecriture de P/C'),
        ('F', 'Payé'),
        ('I', 'Visa comptable'),
        ('J', 'Rejet comptable'),
        ('N', 'Nouveau'),
        ('P', 'Préparation P/C'),
        ('R', 'Rejet CF'),
        ('V', 'Approuvé par le chef'),
        ('W', 'Visa CF'),
        ], 'Etat')
    situation_benef_line = fields.One2many("compta_situation_benef_line", 'situation_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)



    def remplir_situation(self):
        
        val_typeb = int(self.type_beneficiaire)
        val_benef = self.nom_benef.nm
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_titre = int(self.cd_titre_id)
        val_section = int(self.cd_section_id)
        val_chap = int(self.cd_chapitre_id)
        val_art = int(self.cd_article_id)
        val_para = int(self.cd_paragraphe_id)
        val_rub = int(self.cd_rubrique_id)
        
        if self.benef == '1':
            for vals in self:
                vals.env.cr.execute(""" SELECT r.no_ex as exo, c.name as nom, m.no_mandat as numero, m.lb_obj as objet, m.mnt_ord as montant, m.et_doss as etat 
                FROM ref_exercice r, res_company c, budg_mandat m
                WHERE r.id = m.x_exercice_id AND m.x_exercice_id = %s AND c.id = m.company_id AND m.company_id = %s
                AND m.type_beneficiaire_id = %s AND m.no_beneficiaire = %s """ ,(val_ex, val_struct, val_typeb, val_benef))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.situation_benef_line.unlink()
                for line in rows:
                    result.append((0,0, {'no_ex' : line['exo'], 'struct': line['nom'], 'num': line['numero'], 'objet': line['objet'], 'montant': line['montant'], 'etat': line['etat']}))
                self.situation_benef_line = result
                
        elif self.benef == '2':
            for vals in self:
                vals.env.cr.execute(""" SELECT r.no_ex as exo, c.name as nom, m.no_mandat as numero, m.lb_obj as objet, m.mnt_ord as montant, m.et_doss as etat 
                FROM ref_exercice r, res_company c, budg_mandat m
                WHERE r.id = m.x_exercice_id AND m.x_exercice_id = %s AND c.id = m.company_id AND m.company_id = %s""" ,(val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.situation_benef_line.unlink()
                for line in rows:
                    result.append((0,0, {'no_ex' : line['exo'], 'struct': line['nom'], 'num': line['numero'], 'objet': line['objet'], 'montant': line['montant'], 'etat': line['etat']}))
                self.situation_benef_line = result
        
        else:
            for vals in self:
                vals.env.cr.execute(""" SELECT r.no_ex as exo, c.name as nom, m.no_mandat as numero, m.lb_obj as objet, m.mnt_ord as montant, m.et_doss as etat 
                FROM ref_exercice r, res_company c, budg_mandat m, budg_titre bt, budg_section bs, budg_chapitre bc, budg_article ba, budg_paragraphe bp, budg_rubrique br
                WHERE r.id = m.x_exercice_id AND m.x_exercice_id = %s AND c.id = m.company_id AND m.company_id = %s
                AND m.type_beneficiaire_id = %s AND m.no_beneficiaire = %s AND bt.id = %s AND bs.id = %s AND bc.id = %s AND ba.id = %s AND bp.id = %s AND br.id = %s """ ,(val_ex, val_struct, val_typeb, val_benef, val_titre, val_section, val_chap, val_art, val_para, val_rub))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.situation_benef_line.unlink()
                for line in rows:
                    result.append((0,0, {'no_ex' : line['exo'], 'struct': line['nom'], 'num': line['numero'], 'objet': line['objet'], 'montant': line['montant'], 'etat': line['etat']}))
                self.situation_benef_line = result
            

class Compta_situation_benef_line(models.Model):
    _name='compta_situation_benef_line'
    
    situation_id = fields.Many2one('compta_situation_benef', ondelete='cascade')
    no_ex = fields.Char('Exercice', readonly=True)
    struct = fields.Char('Structure', readonly=True)
    num = fields.Char('N°', readonly=True)
    objet = fields.Char('Objet', readonly=True)
    montant = fields.Integer('Montant', readonly=True)
    etat = fields.Char('Etat', readonly=True)
    



class ComptaApprovisionnement(models.Model):
    _name = 'compta_approvisionnement'
    _rec_name = 'nom_caissier'
    
    code_caissier = fields.Char("Code caissier")
    nom_caissier = fields.Char("Nom caissier")
    mnt_encours_total = fields.Integer("Mt total encours")
    encours_num = fields.Integer("En cours numéraire de la caisse")
    approvisionnement_line = fields.One2many('compta_approvisionnement_line', 'approvisionnement_id')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Confirmé'),
        ('P', 'Provisoire'),
        ], string ="Etat", default ='draft', required=True)


class ComptaApprovisionnementLine(models.Model):
    _name = 'compta_approvisionnement_line'
    
    approvisionnement_id = fields.Many2one('compta_approvisionnement', ondelete='cascade')
    code_guichetier = fields.Char("Code guichetier")
    nom_guichetier = fields.Char("Nom guichetier")
    ouvert = fields.Boolean("Ouvert")
    mnt_encours = fields.Integer("En cours-num")
    mnt_recu = fields.Integer("Déjà reçu")
    mnt_a_recevoir = fields.Integer("Mnt à reçevoir")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
  

class ComptaJourGuichet(models.Model):
    _name='compta_jour_guichet'
    _rec_name = 'cd_us_gui'
    
    no_jour = fields.Integer('N° Journée', readonly=True)
    cd_us_gui = fields.Many2one('res.users', string='Guichetier', default=lambda self: self.env.user)
    dt_ouvert = fields.Date('Date ouverture',default=fields.Date.context_today, readonly=True)
    dt_fermeture = fields.Date('Date fermeture')
    mnt_ouverture = fields.Integer('Montant ouverture', readonly=True)
    mnt_fermeture = fields.Integer('Montant fermeture')
    fg_ouvert = fields.Selection([
        ('Y','Oui'),
        ('N','Non')
        ], 'Ouvert ?')
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    state = fields.Selection([
        ('draft','Brouillon'),
        ('O','Ouvert'),
        ('F','Fermé'),       
        ], 'Etat', default='draft')
    etat = fields.Boolean(default=False)
    #user_id = fields.Many2one('res.users', string='user', track_visibilty='onchange', readonly=True,  default=lambda self: self.env.user)

    @api.onchange('cd_us_gui')
    def mtOuvert(self):
        
        val_ex = int(self.cd_us_gui.x_exercice_id)
        val_struct = int(self.company_id)
        val_user = int(self.cd_us_gui)
    
        self.env.cr.execute("""select mnt_rest from compta_versement_guichet where
        no_jour_guichet = (select max(no_jour) from compta_jour_guichet where cd_us_gui = %d and x_exercice_id = %d and company_id = %d) 
        and guichetier = %d and x_exercice_id = %d and company_id = %d""" %(val_user, val_ex, val_struct, val_user, val_ex, val_struct))
        mt = self.env.cr.fetchone()
        self.mnt_ouverture = mt and mt[0] or 0
    


    def OuvertureGuichet(self):
        v_ex = int(self.cd_us_gui.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_user = int(self.cd_us_gui)
        dte_jour = self.dt_ouvert
        v0 = None
        mnt = self.mnt_ouverture
        
        self.env.cr.execute("SELECT count(id) from compta_caisse_struct where company_id = %d and cd_us_caisse = %d" %(val_struct, val_user))
        resu = self.env.cr.fetchone()
        res = resu and resu[0] or 0
        if res != 1:
            raise ValidationError(_("Vous n'êtes pas guichetier. Impossible d'ouvrir une journée."))
            
        """
        self.env.cr.execute(""select count(id) from compta_jour_guichet where company_id = %d and x_exercice_id = %d and cd_us_gui = %d"" %(val_struct, val_ex, val_user))
        resul = self.env.cr.fetchone()
        res1 = resul and resul[0] or 0
        if res1 != 0:
            self.env.cr.execute(""select mnt_fermeture from compta_jour_guichet where x_exercice_id = %s and company_id = %s and cd_us_gui = %s and no_jour = (select max(no_jour) from 
            compta_jour_guichet where x_exercice_id = %s and company_id = %s and cd_us_gui = %s)"" ,(val_ex, val_struct, val_user,val_ex, val_struct, val_user))
            resul2 = self.env.cr.fetchone()
            res2 = resul2 and resul2[0] or 0
            self.mnt_ouverture = res2
        """
        
        
        self.env.cr.execute("""select max(no_jour), state from compta_jour_guichet where company_id = %d and x_exercice_id = %d and cd_us_gui = %d group by state
        """ %(val_struct, val_ex, val_user))
        r = self.env.cr.dictfetchall()

        v_etat = r and r[0]['state']
        if v_etat == 'O':
            raise ValidationError(_("Votre dernière journée de caisse n'est pas fermée. Vous ne pouvez donc pas ouvrir une nouvelle journée."))
        
        self.env.cr.execute("""SELECT distinct no_jour, dt_ouvert, dt_fermeture FROM compta_jour_caisse WHERE company_id = %s AND x_exercice_id = %s and id = (select max(id) from compta_jour_caisse
        WHERE company_id = %s AND x_exercice_id = %s)""",(val_struct, val_ex, val_struct, val_ex))
        res = self.env.cr.dictfetchall()
        var_jr = res and res[0]['no_jour']
        var_dt = res and res[0]['dt_ouvert']
        dt_fermeture = res and res[0]['dt_fermeture']
        
        if dt_fermeture == dte_jour:
            raise ValidationError(_('La caisse est déja fermée. Vous ne pouvez donc pas ouvrir votre guichet.'))
        
        if not(var_jr):
            var_jr = 0
         
        #PREMIERE INSERTION
        if var_jr == 0:
            self.env.cr.execute("""SELECT MAX(no_jour) FROM compta_jour_caisse WHERE company_id = %d AND x_exercice_id = %d""" %(val_struct, val_ex))
            res = self.env.cr.fetchone()
            no_jour_caisse = res and res[0] or 0
        
            self.no_jour = no_jour_caisse + 1
            
            self.env.cr.execute("""SELECT mnt_fermeture FROM compta_jour_caisse WHERE company_id = %d AND x_exercice_id = %d""" %(val_struct, val_ex))
            res1 = self.env.cr.fetchone()
            mnt = res1 and res1[0] or 0
           
        
            self.env.cr.execute("""INSERT INTO compta_jour_caisse (cd_us_caisse, company_id, x_exercice_id, no_jour, dt_ouvert, dt_fermeture, mnt_ouverture, mnt_fermeture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0)""",(val_user, val_struct, val_ex, self.no_jour, self.dt_ouvert, v0, mnt))
            
        
        elif var_dt == self.dt_ouvert:
            self.env.cr.execute("""SELECT MAX(no_jour) FROM compta_jour_caisse WHERE company_id = %s AND x_exercice_id = %s""" ,(val_struct, val_ex))
            resu = self.env.cr.fetchone()
            no_jour = resu and resu[0] or 0
            self.no_jour = no_jour
            self.env.cr.execute("UPDATE compta_jour_caisse SET mnt_ouverture = mnt_ouverture + %s WHERE no_jour = %s AND company_id = %s AND x_exercice_id = %s",(mnt, no_jour, val_struct, val_ex))


        elif var_jr != 0 and var_dt != self.dt_ouvert:
            self.env.cr.execute("""SELECT MAX(no_jour) FROM compta_jour_caisse WHERE company_id = %s AND x_exercice_id = %s""" ,(val_struct, val_ex))
            res1 = self.env.cr.fetchone()
            no_caisse = res1 and res1[0] or 0
            self.no_jour = no_caisse + 1
                   
            self.env.cr.execute("""INSERT INTO compta_jour_caisse (cd_us_caisse, company_id, x_exercice_id, no_jour, dt_ouvert, dt_fermeture, mnt_ouverture, mnt_fermeture)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0)""",(val_user, val_struct, val_ex, self.no_jour, self.dt_ouvert, v0, self.mnt_ouverture))

        self.write({'state': 'O'})
             
    
      
class ComptaVersementGuichet(models.Model):
    _name = "compta_versement_guichet"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    no_jour_caisse = fields.Integer("N° Jour Caisse")
    no_jour_guichet = fields.Integer("N° Jour Guichet")
    no_oper = fields.Integer("N° Opération")
    mnt_verse_caisse = fields.Float("Montant versé")
    mnt_rest = fields.Float("Montant reste")
    guichetier = fields.Many2one("res.users")
    
class ComptaReversement(models.Model):
    _name = "compta_reversement"
    
    name = fields.Char("Nom", default="Reversement")
    caissier = fields.Many2one("compta_caisse_struct", default=lambda self:self.env['compta_caisse_struct'].search([('fg_resp','=',True)]), string="Caissier principal", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    mnt_total = fields.Float("Mnt en cours total", readonly=True)
    no_jour = fields.Integer()
    dt_ouvert = fields.Date('Date ouverture',default=fields.Date.context_today, readonly=False)
    reversement_ids = fields.One2many("compta_reversement_line", "reversement_id")
    guichetier = fields.Many2one("compta_caisse_struct",domain="[('cd_us_caisse','=', user_id)]",required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True, default=lambda self: self.env.user)
    etat = fields.Selection([
        ('draft', 'Brouillon'),
        ('I', 'Initialisé'),
        ('F', 'Fait')
        ],string="Etat", default='draft')
    
    def initialiser(self):
        
        val_ex = int(self.user_id.x_exercice_id)
        print("exercice", val_ex)
        val_struct = int(self.company_id)
        print("structure", val_struct)
        v_id = int(self.guichetier.cd_us_caisse)
        v1_id = int(self.guichetier)
        print("guichetier", v1_id)
        v_dte = self.dt_ouvert
        
        self.env.cr.execute("""select no_jour as jour from compta_jour_guichet where dt_ouvert = %s and company_id = %s and cd_us_gui = %s""", (v_dte, val_struct, v_id))
        jr = self.env.cr.fetchone()
        self.no_jour = jr and jr[0] or 0
        v_jr = self.no_jour
    
        for vals in self:
            vals.env.cr.execute("""select (sum( case when u.type_operation = 1 then l.mnt_op_cpta end) - coalesce(sum( case when u.type_operation = 2 then l.mnt_op_cpta end),0)) as encours, r.id as code,
            p.id as guichetier, u.no_jour as jour from compta_guichet_line l, compta_guichet_unique u, res_users r, res_partner p, compta_caisse_struct c
            where u.modreg = '0' and p.id = r.partner_id and u.id = l.guichet_id and u.no_jour = %s and c.id = %s
            and r.id = u.gui_us and l.company_id = %s and u.date_ope = %s and l.fg_etat <> 'A' group by r.id,p.id, u.no_jour """,(v_jr,v1_id,val_struct, v_dte))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.reversement_ids.unlink()
            for line in rows:
                result.append((0,0, {'code' : line['code'], 'guichetier' : line['guichetier'], 'encours': line['encours'], 'no_jour': line['jour']}))
            self.reversement_ids = result
            
        self.write({'etat': 'I'})
    
    def reverser(self):
        
        v_ex = int(self.user_id.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)

        val_struct = int(self.company_id)
        v1_id = int(self.guichetier)
        v_jr = int(self.no_jour)
        v_id = int(self.guichetier.cd_us_caisse)
        
        self.env.cr.execute("select max(no_oper + 1) from compta_versement_guichet where x_exercice_id = %d and company_id = %d and no_jour_guichet = %d and no_jour_caisse =%d and guichetier = %d" %(val_ex, val_struct, v_jr, v_jr, v1_id))
        res = self.env.cr.fetchone()
        r = res and res[0] or 0
        
        if not(r):           
            val_op = 1
        else:
            val_op = r
        
        for record in self.reversement_ids:
            if record.mntverser > record.encours:
                raise ValidationError(_("Montant de reversement erroné"))
            elif record.mntverser == 0:
                return None 
        
            self.env.cr.execute("""INSERT INTO compta_versement_guichet (x_exercice_id, company_id, no_jour_caisse, no_jour_guichet, no_oper, guichetier, mnt_verse_caisse, mnt_rest)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""" ,(val_ex, val_struct, v_jr, v_jr, val_op, v_id, record.mntverser, record.mnt_rest))

        self.write({'etat': 'F'})
        
class ComptaReversementLine(models.Model):
    _name = "compta_reversement_line"

    reversement_id = fields.Many2one("compta_reversement",ondelete='cascade')
    code = fields.Many2one("res.users", readonly=True)
    guichetier = fields.Many2one("res.partner", readonly=True)
    ouvert = fields.Boolean("Ouvert",default=True)
    encours = fields.Float("En cours num", readonly=True)
    dejaencaisse = fields.Float("Déjà encaissé", readonly=True)
    mntverser = fields.Float("Mnt à reverser")
    no_jour = fields.Integer()
    mnt_rest = fields.Float("Reste dans la caisse", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    @api.onchange('mntverser')
    def cal(self):
        
        for x in self:
            x.mnt_rest = x.encours - x.mntverser
  

class ComptaJourCaisse(models.Model):
    _name='compta_jour_caisse'
    _rec_name = 'no_jour'
    
    no_jour = fields.Integer('N° Journée', readonly=True)
    cd_us_caisse = fields.Many2one('res.users', string='Caissier', track_visibilty='onchange', default=lambda self: self.env.user)
    dt_ouvert = fields.Date('Date ouverture',default=fields.Date.context_today, readonly=True)
    dt_fermeture = fields.Date('Date fermeture')
    mnt_ouverture = fields.Integer('Montant ouverture')
    mnt_fermeture = fields.Integer('Montant fermeture')
    caisse_struct_line = fields.One2many('compta_caisse_struct','jour_caisse')
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaCaisseStruct(models.Model):
    _name = "compta_caisse_struct"
    _rec_name = 'cd_us_caisse'
    
    jour_caisse = fields.Many2one('compta_jour_caisse')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    dt_debut = fields.Date("En activité depuis le", required=True)
    dt_fin = fields.Date("Fin d'activité le")
    fg_actif = fields.Boolean("Actif")
    fg_resp = fields.Boolean("Resp. Caisse")
    fg_mode = fields.Selection([
        ('C', 'Caisse'),
        ('N', 'Non')
        ], 'Mode')
    fg_ecr = fields.Boolean("Ecriture")
    cd_us_caisse = fields.Many2one('res.users', string='Utilisateur', required = True)
    code = fields.Char("Code", readonly=True)
    no_guichet = fields.Integer('')
    
    @api.onchange('cd_us_caisse')
    def Code(self):
        if self.cd_us_caisse:
            self.code = self.cd_us_caisse.login
    
    
    
class ComptaGuichetUnique(models.Model):
    _name = "compta_guichet_unique"
    _rec_name = 'no_op'
    
    no_op = fields.Integer("N° Opération", readonly=True)
    no_ecr = fields.Integer("N° Ecriture", readonly=True)
    type_operation = fields.Many2one("compta_data", 'Type OP. Guichet', default=lambda self: self.env['compta_data'].search([('cd_data','=', 'E')]),required=True, states={'C': [('readonly', True)], 'P': [('readonly', True)], 'A': [('readonly', True)]})
    val = fields.Integer()
    journal_id = fields.Many2one("compta_type_journal", 'Type de Journal', required = False, states={'C': [('readonly', True)], 'P': [('readonly', True)], 'A': [('readonly', True)]})
    contact = fields.Char("Contact", states={'P': [('readonly', True)], 'A': [('readonly', True)]})
    nom_usager = fields.Char("Nom Usager", states={'P': [('readonly', True)], 'A': [('readonly', True)]})
    mode_reglement = fields.Many2one("compta_jr_modreg", "Mode de règlement", required=True, states={'P': [('readonly', True)], 'A': [('readonly', True)]})
    type_op = fields.Char(default = 'G')
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture')
    type_quittance = fields.Many2one("compta_type_quittance", 'Type quittance')
    var_jr = fields.Integer()
    fg_sens = fields.Char(size=1)
    var_cpte = fields.Integer()
    val_lecr = fields.Integer()
    mnt_total = fields.Integer("Montant")
    type_quittance = fields.Many2one("compta_type_quittance")
    date_ope = fields.Date("Date",default=fields.Date.context_today, readonly=True)
    dte = fields.Date("Date",default=fields.Date.context_today)
    compte = fields.Char('Compte')
    no_jour = fields.Integer()
    modreg = fields.Char()
    quittance_id = fields.Many2one("compta_quittance_unique")
    cheque_id = fields.Many2one("compta_cheque_rec")
    numero = fields.Char("Réf. chèque")
    mnt_encours = fields.Float("En cours", readonly=True)
    gui_us = fields.Many2one('res.users',default=lambda self: self.env.user)
    guichet_line = fields.One2many("compta_guichet_line", "guichet_id", states={'C': [('readonly', True)], 'P': [('readonly', True)], 'A': [('readonly', True)]})
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('C', 'Provisoire'),
        ('P', 'Confirmé'),
        ], string ="Etat", default ='draft', required=True)
    facture = fields.Many2one("compta_facturation","Facture", domain=['|',('etat', '=', 'V'),('etat', '=', 'PP')],required=False)
    factures = fields.Char("Facture")
    encour = fields.Boolean("Voir encours", default = True)
    dte_f = fields.Date("Date facture", readonly=True)
    ref_f = fields.Char(readonly=False)

    # Récupérer l'exercice de l'utilisateur poour effectuer les traitements sur ça
    @api.onchange('gui_us')
    def User(self):
        if self.gui_us:
            self.x_exercice_id = self.gui_us.x_exercice_id

    @api.onchange('facture')
    def remp(self):
        for x in self:
            if x.facture:
                x.nom_usager = x.facture.client_id.nm_rs
                x.contact = x.facture.telephone
                x.dte_f = x.facture.dte
    
    
    @api.onchange('type_operation')
    def typeope(self):
        if self.type_operation.cd_data == 'D':
            self.env.cr.execute("select id from compta_jr_modreg where name = 1")
            res = self.env.cr.fetchone()
            self.mode_reglement = res and res[0] or 0
            self.env.cr.execute("select id from compta_type_ecriture where type_ecriture = 'D' ")
            res1 = self.env.cr.fetchone()
            self.type_ecriture = res1 and res1[0] or 0
        else:
            self.env.cr.execute("select id from compta_type_ecriture where type_ecriture = 'E' ")
            res2 = self.env.cr.fetchone()
            self.type_ecriture = res2 and res2[0] or 0
            
            
            
    
    @api.onchange('encour')
    def OnchangeMnt(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        dt = self.dte
        v_gui = int(self.gui_us)
        print("guichetier", v_gui)
        self.env.cr.execute("select distinct no_jour from compta_guichet_unique where dte = %s and company_id = %s and x_exercice_id = %s" ,(dt, val_struct, val_ex))
        j = self.env.cr.fetchone()
        jr = j and j[0] or 0
        print("jour", jr)
        
        if self.encour == True:
            self.env.cr.execute("""select sum(g.mnt_op_cpta)
            from compta_guichet_line g, compta_guichet_unique u
            where u.id = g.guichet_id and u.no_jour = %s
            and u.type_operation = 1 and date_ope = %s and u.gui_us = %s 
            and u.state not in ('draft', 'A') and u.company_id = %s  """ ,(jr, dt, v_gui, val_struct))
            res = self.env.cr.fetchone()
            self.mnt_encours = res and res[0] or 0
    
    
    #fonction pour ramener le compte selon le mode de reglement
    @api.onchange('mode_reglement')
    def remplir_champ(self):

        #self.var_jr = self.mode_reglement.journal_id.id  
        self.var_cpte = self.mode_reglement.souscpte
        self.modreg = self.mode_reglement.name.mode_reg
        self.type_quittance = self.mode_reglement.type_quittance
    
    
    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        
    def generer_ecriture_guichet(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        id_guichet = self.id
        var_jrs = int(self.var_jr)
        var_cptes = int(self.var_cpte)
        val_date = str(self.dte)
        
        
        #self.write({'state': 'P'})
        
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
       
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.guichet_line:
                no_ecrs1 = no_ecrs1 + 1
                if record.tvas == True:
                    record.ecr_tvas = no_ecrs1
                    record.no_lecr = record.ecr_tvas + 1
                else:
                    record.no_lecr = no_ecrs1 + 1
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            print("Valeur",self.no_ecr)
            #no_ecrs11 = no_ecrs1 + 1
            #no_ecrs1= no_ecrs11
            #self.val_lecr = no_ecrs11
            for record in self.guichet_line:
                self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
                noecr = self.env.cr.dictfetchall()
                no_ecrs = noecr and noecr[0]['no_ecr']
                no_ecrs1 = noecr and noecr[0]['no_lecr']
                no_ecr = no_ecrs
                
                #self.no_ecr = no_ecr + 1
                
                no_ecrs11 = no_ecrs1 + 1
                no_ecrs1= no_ecrs11
                
                if record.tvas == True:
                    record.ecr_tvas = no_ecrs1
                    record.no_lecr = record.ecr_tvas + 1
                else:
                    record.no_lecr = no_ecrs1
                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
        for record in self.guichet_line:
            val = (self.no_ecr)
            val_id = (self.id)
            val_cpte = (self.var_cpte)
            v_lecr = (record.no_lecr)
            print("lecr",v_lecr)
            self.env.cr.execute("UPDATE compta_guichet_line SET no_ecr = %s, compte = %s, var_jr = %s, var_lecr = %s WHERE guichet_id = %s" ,(val, val_cpte, var_jrs, v_lecr, val_id))

        
    @api.multi
    def action_confirmer(self):

        val_struct = int(self.company_id)
        v_user = int(self.gui_us)
        v_id = int(self.id)
        dt = self.date_ope
        v_fac = int(self.facture)
        print("id facture", v_fac)

        v_ex = int(self.gui_us.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)

        self.ref_f = str(self.facture.num_facture) + 'du' + str(self.dte_f)
        
        self.env.cr.execute("""select count(cd_us_caisse) from compta_caisse_struct where company_id = %d and cd_us_caisse = %d""" %(val_struct,v_user))
        res = self.env.cr.fetchone()
        resu = res and res[0] or 0
        
        if resu == 0:
            raise ValidationError(_("Vous n'êtes pas déclarés comme guichetier. Veuillez contacter l'administrateur")) 
        
        
        self.env.cr.execute("select distinct g.state from compta_jour_guichet g, compta_guichet_unique u where u.date_ope = g.dt_ouvert and u.company_id = %d and g.state = 'O'" %(val_struct))
        et = self.env.cr.fetchone()
        etat = et and et[0] or 0
        
        if etat != 'O':
            raise ValidationError(_("Votre guichet n'est pas ouvert"))    
        
        self.env.cr.execute("select numop from compta_compteur_guichet where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        nu_op = self.env.cr.fetchone()
        numop = nu_op and nu_op[0] or 0
        c1 = int(numop) + 1
        c = str(numop)
        if c == "0":
            ok = str(c1).zfill(4)
            self.no_op = ok
            vals = c1
            self.env.cr.execute("""INSERT INTO compta_compteur_guichet(x_exercice_id,company_id,numop) VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))    
        else:
            c1 = int(numop) + 1
            c = str(numop)
            ok = str(c1).zfill(4)
            self.no_op = ok
            vals = c1
            self.env.cr.execute("UPDATE compta_compteur_guichet SET numop = %d WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))


        self.env.cr.execute("select distinct g.no_jour from compta_jour_guichet g, compta_guichet_unique u where g.dt_ouvert = '%s' and u.company_id = %s and u.x_exercice_id = %s" %(dt,val_struct, val_ex) )
        jr = self.env.cr.fetchone()
        jour = jr and jr[0] or 0
        self.no_jour = jour
        
        #self.generer_ecriture_guichet()
        
        self.env.cr.execute("""SELECT sum(mnt_op_cpta) FROM compta_guichet_line WHERE guichet_id = %d and company_id = %d""" %(v_id, val_struct))
        som = self.env.cr.fetchone()
        somme = som and som[0] or 0
        self.mnt_total = somme
        
        for vals in self.guichet_line:
            vals.x_exercice_id = val_ex
            val_t = vals.ref_pj
            if vals.pj.libelle.refe == '62':
                self.env.cr.execute("update budg_titrerecette set et_doss = 'F' where x_exercice_id = %s and company_id = %s and cd_titre_recette = %s" ,(val_ex, val_struct, val_t))
            if vals.pj.libelle.refe == '31':
                self.env.cr.execute("update budg_mandat set state = 'F' where x_exercice_id = %s and company_id = %s and no_mandat = %s" ,(val_ex, val_struct, val_t))
            
        if self.fg_sens == 'D':
            for x in self.guichet_line:
                x.fg_sens = 'C'
        else:
            for x in self.guichet_line:
                x.fg_sens = 'D'
        
        self.env.cr.execute("""SELECT sum(mnt_op_cpta) FROM compta_guichet_line WHERE guichet_id = %d and x_exercice_id = %d and company_id = %d""" %(v_id, val_ex, val_struct))
        som = self.env.cr.fetchone()
        somme_ht = som and som[0] or 0
        print("somme total ligne",somme_ht)
        
        self.env.cr.execute("""SELECT distinct f.reste FROM compta_facturation f WHERE f.id = %d """ %(v_fac))
        som = self.env.cr.fetchone()
        somme_total = som and som[0] or 0
        print("somme total reste",somme_total)
        
        if somme_ht != somme_total:    
            
            for x in self.guichet_line:
                val = int(x.mnt_ht)
                print("val mt ht",val)
                val_t1 = int(x.type1)
                print("val type1",val_t1)
                val_t2 = int(x.type2)
                print("val type2",val_t2)
                #x.env.cr.execute("""update compta_facturation_ligne set prix = prix - %d where facture_id_def = %d and type1 = %d and type2 = %d""" %(val, v_fac, val_t1, val_t2))
            
            self.env.cr.execute("""update compta_facturation set etat = 'PP', reste = reste - %s where id = %s""" ,(somme_ht, v_fac))
        
        else:
            self.env.cr.execute("""update compta_facturation set etat = 'P', reste = reste - %s where id = %s""" ,(somme_ht,v_fac,))

            
        
        self.write({'state': 'C'})
    
    
    def AfficherLigne(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.facture)
        
        for vals in self:
            vals.env.cr.execute(""" SELECT * 
            FROM compta_facturation_ligne l, compta_facturation f
            WHERE f.id = l.facture_id_def AND l.facture_id_def = %d AND l.x_exercice_id = %d AND l.company_id = %d""" %(v_id,val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.guichet_line.unlink()
            for line in rows:
                result.append((0,0, {'x_exercice_id' : line['x_exercice_id'], 'company_id': line['company_id'], 'type1': line['type1'], 'type2': line['type2'], 'id_imput': line['id_imput'], 'mnt_ht': line['prix']}))
            self.guichet_line = result

            
    @api.onchange('type_operation')
    def type_sens(self):
        if self.type_operation.cd_data == 'E':
            self.fg_sens = 'D'
            for x in self.guichet_line:
                x.vals = 'E'
        else:
            self.fg_sens = 'C'
            for x in self.guichet_line:
                x.vals = 'D'

            
        
class ComptaGuichetLine(models.Model):
    _name = "compta_guichet_line"
    
    val = fields.Integer()
    vals = fields.Char()
    guichet_id = fields.Many2one("compta_guichet_unique", ondelete='cascade')
    no_ecr = fields.Integer("N° ecriture", readonly=True)
    no_lecr = fields.Integer("N° Ligne", readonly=True)
    typ_pj = fields.Many2one("compta_piece", string='Pièce Just.', required=False)
    pj = fields.Many2one('compta_piece_line', 'Pièce Just.', domain="[('type2','=',type2)]", required=False)
    typ1_pj = fields.Selection([
        ('M', 'Mandat'),
        ('OP', 'Ordre de paiement'),
        ('R', 'Recette')
        ], string='Pièce Just.')
    an_pj = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Année")
    ref_pj = fields.Char("Ref. Pj")
    ref0_pj = fields.Many2one("budg_mandat", domain=[('state', '=', 'E')], string = "Ref. Mdt")
    ref1_pj = fields.Many2one("budg_op", domain=[('et_doss', '=', 'V')], string = "Ref. OP")
    ref2_pj = fields.Many2one("budg_titrerecette", domain=[('et_doss', '=', 'E')], string = "Ref. Rec")
    mnt_op_cpta = fields.Float("Montant TTC", readonly=False)
    mnt_ht = fields.Float('Montant HT', required=True)
    mnt_tva = fields.Float('Montant TVA', readonly=False)
    tvas = fields.Boolean(string='TVA ?', default=False)
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", required=True, domain=[('code', '=like', 'E%')])
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature d'opération", domain="[('typebase_id','=',type1), ('fg_guichet','=',True)]", required=True)
    code1 = fields.Char()
    code2 = fields.Char()
    type1_op_cpta = fields.Many2one("compta_type1_op_cpta","Catégorie d'opération", required=False)
    type2_op_cpta = fields.Many2one("compta_reg_op_guichet_unique","Nature opération", required=False)
    #id_tlv = fields.Selection(selection = 'get_imputation', string = 'Nature détaillée')
    id_tlv = fields.Many2one("compta_table_listnat", string = 'Nature détaillée')
    compte = fields.Integer()
    var_lecr = fields.Integer()
    ecr_tvas = fields.Integer()
    var_jr = fields.Integer()
    cd_nat = fields.Char()
    id_imput = fields.Integer()
    id_imput_tva = fields.Integer()
    no_imputation = fields.Char('Imputation')
    fg_etat = fields.Selection([
        ('P', 'Provisoire'),
        ('V', 'Vérifié'),
        ('A', 'Annulé'),
        ('R', 'Rejété')], 'Etat', default='P')
    fg_sens = fields.Char('Sens')
    dte_op = fields.Date(default=fields.Date.context_today)
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('tvas','mnt_ht')
    def tva(self):
        val_struc = int(self.company_id)
        for x in self:
            if x.tvas == False:
                x.mnt_tva = 0
                x.mnt_op_cpta = x.mnt_ht * 1
            elif x.tvas == True: 
                x.env.cr.execute("select taux, compte_id FROM compta_param_tva WHERE company_id = %d" %(val_struc))
                
                res = self.env.cr.dictfetchall()
                tau  = res and res[0]["taux"]
                self.id_imput_tva  = res and res[0]["compte_id"]
                
                taux = tau/100
                print("taux tva", taux)
                
                x.mnt_tva = round(x.mnt_ht * taux)
                x.mnt_op_cpta = x.mnt_ht + x.mnt_tva
    
    
    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2 :
                val.code2 = val.type2.type_opcpta1
    
    @api.onchange('type1')
    def Cod1(self):
        for val in self:
            if val.type1 :
                val.code1 = val.type1.code

    @api.onchange('ref0_pj')
    def MontantMandat(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_mdt = int(self.ref0_pj.id)
        
        self.env.cr.execute("""select mnt_ord from budg_mandat where id = %d and
        company_id = %d and x_exercice_id = %d""" %(val_mdt, val_struct, val_ex))
        res = self.env.cr.fetchone()
        res1 = res and res[0] or 0
        
        for val in self:
            if self.ref_pj:
                self.mnt_op_cpta = res1
                
        
    @api.onchange('ref1_pj')
    def MontantOrdrePaiement(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_op = int(self.ref1_pj.id)
        
        self.env.cr.execute("""select mnt_op from budg_op where id = %d and
        company_id = %d and x_exercice_id = %d""" %(val_op, val_struct, val_ex))
        ress = self.env.cr.fetchone()
        res2 = ress and ress[0] or 0
        
        for val in self:
            if self.ref1_pj:
                self.mnt_op_cpta = res2
    
    
    @api.onchange('ref2_pj')
    def MontantRecette(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_op = int(self.ref2_pj.id)
        
        self.env.cr.execute("""select mnt_rec from budg_titrerecette where id = %d and
        company_id = %d and x_exercice_id = %d""" %(val_op, val_struct, val_ex))
        resss = self.env.cr.fetchone()
        res3 = resss and resss[0] or 0
        
        for val in self:
            if self.ref2_pj:
                self.mnt_op_cpta = res3
                

    @api.onchange('type2','type1')
    @api.model
    def get_imputation(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_type1 = int(self.type1.id)
        val_type2 = str(self.code2)
       
        #self.env.cr.execute("""select R.souscompte_id, R.fg_term from  compta_reg_op_guichet_unique R where R.type1_opcpta = %d and R.id = %d and R.x_exercice_id = %d and R.company_id = %d""" %(val_type1,val_type2, val_ex, val_struct))
        #Nouvelle requete
        self.env.cr.execute("""select r.souscompte_id, r.fg_term from compta_type_op_cpta r where r.typebase_id = %s and type_opcpta1 = %s""" ,(val_type1,val_type2))
        #self.env.cr.execute("""select CD_NAT, LB_NAT, LV_NAT FROM "+" V_NM_TLV +" WHERE " + V_WH_TLV .concate_souscpte, R.fg_term from  compta_reg_op_guichet_unique R, ref_souscompte C where R.type1_opcpta = %d and R.no_imputation = C.id and R.id = %d """ %(val_type1,val_type2))
        
        imput = self.env.cr.dictfetchall()
        terminal  = imput and imput[0]["fg_term"]
        if val_type1 != False and val_type2 != False:
            
            #if terminal == 'T':
            self.id_imput = imput and imput[0]["souscompte_id"]
            #else:
                #if val_type2 != False:                                       
                    #self.env.cr.execute("""select nm_listnat, clause_where from compta_table_listnat where id = 1 """ )
                    #res = self.env.cr.dictfetchall()
                    #nom_vue = res and res[0]["nm_listnat"]
                    #clause_w = res and res[0]["clause_where"] 
                    #self.env.cr.execute("select cd_nat, lb_nat from %s where  %s" %(nom_vue,clause_w))
                    #nature = self.env.cr.dictfetchall()
                    #return [(x.cd_nat, x.lb_nat) for x in nature]
                    #print('valeur nature',nature)
            #return nature
                    #nature = self.env['compta_colonne_caisse'].search([])
                    #return [(x.cd_col_caise, x.lb_court) for x in nature]
                    #self.no_imputation = nature and nature[0]["vl_nat"]
                    #print('la val imputation',self.no_imputation)
    #id_tlv = fields.Selection(selection = get_imputation, string= 'Nature éventuelle')
   
    
    @api.depends('mnt_op_cpta')
    def EnCours(self):
        
        for record in self:
            self.guichet_id.mnt_encours = self.guichet_id.mnt_encours + self.mnt_op_cpta
    

class ComptaFermeCaisse(models.Model):
    _name = 'compta_ferme_caisse'
    
    name = fields.Char("nom", default='Fermeture caisse')
    type_op = fields.Char('G')
    no_jour = fields.Integer("Journée N°", readonly=True)
    cd_us_caissier = fields.Char("Code caissier")
    dte_jour = fields.Date(default=fields.Date.context_today)
    solde_op = fields.Float("Solde opération (numéraire)", readonly=True)
    nom_caissier = fields.Many2one("compta_caisse_struct",default=lambda self: self.env['compta_caisse_struct'].search([('fg_resp','=', True)]), readonly= True, string="Nom caissier responsable")
    mnt_ouverture = fields.Integer("Montant ouverture de la caisse", readonly=True)
    mnt_fermeture = fields.Integer("Montant fermeture de la caisse", readonly=True)
    ferme_caisse_line = fields.One2many('compta_ferme_caisse_line', 'ferme_caisse_id', readonly=True)
    user_id = fields.Many2one('res.users', string='Caissier', default=lambda self: self.env.user)
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    etat = fields.Selection([
        ('O', 'Ouverte'),
        ('F','Fermée')
        ], string="Etat", default='O')

    @api.onchange('dte_jour')
    def mntOuvert(self):
        v_ex = int(self.user_id.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)

        val_struct = int(self.company_id)
        v_dte = self.dte_jour
        
        self.env.cr.execute("select distinct g.no_jour from compta_jour_guichet g, compta_guichet_unique u where u.date_ope = g.dt_ouvert and g.dt_ouvert = %s and u.company_id = %s" ,(v_dte, val_struct))
        jr = self.env.cr.fetchone()
        self.no_jour = jr and jr[0] or 0
            
        v_jr = int(self.no_jour)
        
        self.env.cr.execute("""select mnt_ouverture from compta_jour_caisse where no_jour = %s and company_id = %s and x_exercice_id = %s""",(v_jr, val_struct, val_ex))   
        resultat = self.env.cr.fetchone()
        self.mnt_ouverture = resultat and resultat[0] or 0
    
    def action_afficher(self):
        
        val_ex = int(self.user_id.x_exercice_id)

        self.x_exercice_id = val_ex
        v_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_dte = self.dte_jour
        v_id = int(self.user_id)
        ids = int(self.id)
        
        self.env.cr.execute("select count(cd_us_caisse)from compta_caisse_struct where fg_resp = True and cd_us_caisse = %s and company_id = %s" ,(v_id, val_struct))
        resul= self.env.cr.fetchone()
        re = resul and resul[0] or 0
        if re == 0:
            raise ValidationError(_('Cette opération est réservée au principal'))
        """
        self.env.cr.execute("select distinct g.no_jour from compta_jour_guichet g, compta_guichet_unique u where u.date_ope = g.dt_ouvert and u.company_id = %s and u.x_exercice_id = %s" ,(val_struct, val_ex) )
        jr = self.env.cr.fetchone()
        self.no_jour = jr and jr[0]
        """  
        v_jr = int(self.no_jour)
        
        

        for vals in self:
            vals.env.cr.execute("""select distinct j.cd_us_gui as guichetier, j.mnt_ouverture as ouverture, j.state as etat, 
            (select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.id = l.guichet_id and u.company_id = %s and u.x_exercice_id = %s and u.no_jour = %s and u.type_operation = 1 and l.fg_etat <> 'A') as encaisse,
            (select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.id = l.guichet_id and u.company_id = %s and u.x_exercice_id = %s and u.no_jour = %s and u.type_operation = 2 and l.fg_etat <> 'A') as decaisse,
            ((select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.id = l.guichet_id and u.company_id = %s and u.x_exercice_id = %s and u.no_jour = %s and u.type_operation = 1 and l.fg_etat <> 'A') - (select sum(l.mnt_op_cpta) 
            from compta_guichet_unique u, compta_guichet_line l where u.id = l.guichet_id and u.company_id = %s and u.x_exercice_id = %s and u.no_jour = %s and u.type_operation = 2 and l.fg_etat <> 'A')) as solde from compta_guichet_line l, compta_guichet_unique gu, compta_jour_guichet j 
            where l.x_exercice_id = %s and l.company_id = %s and gu.date_ope = j.dt_ouvert and j.cd_us_gui = gu.gui_us and gu.id = l.guichet_id and j.no_jour = gu.no_jour and gu.no_jour = %s and l.fg_etat <> 'A' group by j.cd_us_gui, j.mnt_ouverture, j.state"""
            ,(val_struct, v_ex, v_jr, val_struct, v_ex, v_jr, val_struct, v_ex, v_jr, val_struct, v_ex, v_jr,v_ex, val_struct, v_jr))
            
            
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.ferme_caisse_line.unlink()
            for line in rows:
                result.append((0,0, {'nom_guichetier' : line['guichetier'], 'solde_guichet': line['solde'], 'ferme': line['etat'], 'mt_ouverture': line['ouverture'], 'totalencaisse': line['encaisse'], 'totaldecaisse': line['decaisse']}))
            self.ferme_caisse_line = result
           
        
        
        self.env.cr.execute("""select coalesce(sum(case when gu.type_operation = 1 then l.mnt_op_cpta end),0) - coalesce(sum(case when gu.type_operation = 2 then l.mnt_op_cpta end),0) as solde 
        from compta_guichet_line l, compta_guichet_unique gu where l.x_exercice_id = %s and l.company_id = %s and
        gu.id = l.guichet_id and gu.no_jour = %s and gu.modreg = '0' and l.fg_etat <> 'A' """ ,(val_ex, val_struct, v_jr))
                
        res = self.env.cr.fetchone()
        self.solde_op = res and res[0] or 0
        
        self.env.cr.execute("""select sum(l.mnt_op_cpta) from compta_guichet_line l, compta_guichet_unique g 
        where g.id = l.guichet_id and g.company_id = %d and g.x_exercice_id = %d and g.no_jour = %d and l.fg_etat <> 'A' ;""" %(val_struct, val_ex, v_jr))
        res1 = self.env.cr.fetchone()
        val = res1 and res1[0] or 0
        
        self.mnt_fermeture = val + self.mnt_ouverture
        
    def fermer_guichet(self):

        v_ex = int(self.user_id.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex= int(self.x_exercice_id)

        val_struct = int(self.company_id)
        v_dte = self.dte_jour

        #Parce que c'est une seule caisse
        v_mnt = self.mnt_fermeture
        
        for x in self.ferme_caisse_line:
            val_user = x.nom_guichetier.id
            #v_mnt = x.solde_guichet
            self.env.cr.execute("""UPDATE compta_jour_guichet SET state ='F', mnt_fermeture = %s, dt_fermeture = %s WHERE
            state ='O' and cd_us_gui = %s and company_id = %s and x_exercice_id = %s""" ,(v_mnt,v_dte,val_user,val_struct,val_ex))
    
    def generer_ecr_guichet(self):

        v_ex = int(self.user_id.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)

        val_struct = int(self.company_id)
        v_jr = int(self.no_jour)
        v_dte = self.dte_jour

        self.env.cr.execute("""select u.* from compta_guichet_unique u, compta_jour_guichet j where u.no_jour = j.no_jour and u.company_id = %s and u.x_exercice_id = %s and u.no_jour = %s and u.gui_us = j.cd_us_gui
        and u.state = 'C' """,(val_struct,val_ex, v_jr))
        for line in self.env.cr.dictfetchall():
            v_id = line['id']
            type_ecr = line['type_ecriture']
            typ_op = line['type_operation']
            v_mnt = line['mnt_total']
            sens = line['fg_sens']
            cpte = line['var_cpte']
            etat = line['state']

            if etat == 'C':
            
                self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
                noecr = self.env.cr.dictfetchall()
                no_ecrs = noecr and noecr[0]['no_ecr']
                no_ecrs1 = noecr and noecr[0]['no_lecr']
                no_ecr = no_ecrs

                if not(no_ecr):
                    no_ecr = 1
                    no_ecrs1 = 1
                    lecr = no_ecrs1
                    self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture,type_ecriture, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, 'G', %s, %s, 'P')" ,(no_ecr, v_dte, type_ecr, val_ex, val_struct))

                    self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'P') """ ,(no_ecr,lecr, cpte, v_mnt,val_ex, val_struct, sens, v_dte))

                    self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_ex,val_struct, no_ecr, lecr))

                    self.env.cr.execute("UPDATE compta_guichet_unique SET state = 'P' WHERE x_exercice_id = %d and company_id = %d and id = %d" % (val_ex, val_struct, v_id))

                    self.env.cr.execute("UPDATE compta_guichet_line SET no_ecr = %s where company_id = %s and x_exercice_id = %s and dte_op = %s",(no_ecr, val_struct, val_ex, v_dte))

                    self.env.cr.execute("""select l.* from compta_guichet_line l, compta_guichet_unique u where u.company_id = %s and u.x_exercice_id = %s 
                    and l.guichet_id = u.id and l.guichet_id = %s and mnt_op_cpta > 0 and u.state = 'P' and l.fg_etat = 'P' """,(val_struct,val_ex, v_id))
                    for res1 in self.env.cr.dictfetchall():
                        print("resulat ligne",res1)
                        mnt =res1['mnt_ht']
                        print("mnt ligne",mnt)
                        mnt_tva = res1['mnt_tva']
                        print("mnt tva ligne",mnt_tva)
                        imput = res1['id_imput']
                        print("imputation ligne",imput)
                        id_imput_tva = res1['id_imput_tva']
                        print("imputation tva ligne",id_imput_tva)
                        an_pj = res1['an_pj']
                        print("piece ligne",an_pj)
                        #ref = res1['ref_pj']
                        #pj = res1['pj']
                        lsens = res1['fg_sens']
                        #ecr_tva = res1['ecr_tvas']
                        tva = res1['tvas']
                        print("tva ligne",tva)
                        noecr = res1['no_ecr']
                        etat = res1['fg_etat']
                        ids = res1['id']

                        if etat != 'P':
                            raise ValidationError(_("Ecritures déjà générées"))
                        else:

                            self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
                            noecr = self.env.cr.dictfetchall()
                            #no_ecrs = noecr and noecr[0]['no_ecr']
                            no_ecrs1 = noecr and noecr[0]['no_lecr']
                            #no_ecr = no_ecrs

                            no_lecr = no_ecrs1 + 1

                            if tva == True:
                                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, fg_sens, x_exercice_id, company_id, dt_ligne,fg_etat) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 'P')""" ,(no_ecr,no_lecr, id_imput_tva, mnt_tva, lsens, val_ex, val_struct, v_dte))

                                no_lecrs = no_lecr + 1
                                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, fg_sens, x_exercice_id, company_id, dt_ligne,fg_etat) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 'P')""" ,(no_ecr,no_lecrs, imput, mnt, lsens, val_ex, val_struct, v_dte))

                                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecr,no_lecrs,val_ex,val_struct))

                            else:
                                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, fg_sens, x_exercice_id, company_id, dt_ligne,fg_etat) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 'P')""" ,(no_ecr,no_lecr, imput, mnt, lsens, val_ex, val_struct, v_dte))


                                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecr,no_lecr,val_ex,val_struct))

                            self.env.cr.execute("UPDATE compta_guichet_line SET fg_etat = 'V' where guichet_id = %s and company_id = %s and x_exercice_id = %s and id = %s",(v_id, val_struct, val_ex, ids))

                else:
                    no_ecr = no_ecr + 1
                    no_ecrs1 = no_ecrs1 + 1
                    lecr = no_ecrs1
                    self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture,type_ecriture, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, 'G', %s, %s, 'P')" ,(no_ecr, v_dte, type_ecr, val_ex, val_struct))

                    self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'P') """ ,(no_ecr,lecr, cpte, v_mnt,val_ex, val_struct, sens, v_dte))

                    self.env.cr.execute("UPDATE compta_guichet_unique SET state = 'P' WHERE x_exercice_id = %d and company_id = %d and id = %d" % (val_ex, val_struct, v_id))

                    self.env.cr.execute("UPDATE compta_guichet_line SET no_ecr = %s where company_id = %s and x_exercice_id = %s and dte_op = %s",(no_ecr, val_struct, val_ex, v_dte))

                    self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecr,lecr,val_ex,val_struct))

                    self.env.cr.execute("""select distinct l.* from compta_guichet_line l, compta_guichet_unique u where l.company_id = %s and l.x_exercice_id = %s 
                    and u.id = l.guichet_id and l.guichet_id = %s and l.mnt_op_cpta > 0 and l.fg_etat = 'P' and u.state = 'P' """,(val_struct, val_ex, v_id))
                    for res1 in self.env.cr.dictfetchall():
                        print("resulat ligne",res1)
                        mnt =res1['mnt_ht']
                        print("mnt ligne",mnt)
                        mnt_tva = res1['mnt_tva']
                        print("mnt tva ligne",mnt_tva)
                        imput = res1['id_imput']
                        print("imputation ligne",imput)
                        id_imput_tva = res1['id_imput_tva']
                        print("imputation tva ligne",id_imput_tva)
                        an_pj = res1['an_pj']
                        print("piece ligne",an_pj)
                        #ref = res1['ref_pj']
                        #pj = res1['pj']
                        lsens = res1['fg_sens']
                        #ecr_tva = res1['ecr_tvas']
                        tva = res1['tvas']
                        print("tva ligne",tva)
                        #lnoecr = res1['no_ecr']
                        etat = res1['fg_etat']
                        ids = res1['id']

                        if etat != 'P':
                            raise ValidationError(_("Ecritures déjà générées"))
                        else:

                            self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
                            noecr = self.env.cr.dictfetchall()
                            #no_ecrs = noecr and noecr[0]['no_ecr']
                            no_ecrs1 = noecr and noecr[0]['no_lecr']
                            #no_ecr = no_ecrs

                            no_lecr = no_ecrs1 + 1


                            if tva == True:
                                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, fg_sens, x_exercice_id, company_id, dt_ligne,fg_etat) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 'P')""" ,(no_ecr,no_lecr, id_imput_tva, mnt_tva, lsens, val_ex, val_struct, v_dte))

                                no_lecrs = no_lecr + 1
                                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, fg_sens, x_exercice_id, company_id, dt_ligne,fg_etat) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 'P')""" ,(no_ecr,no_lecrs, imput, mnt, lsens, val_ex, val_struct, v_dte))

                                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecr,no_lecrs,val_ex,val_struct))

                            else:
                                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, fg_sens, x_exercice_id, company_id, dt_ligne,fg_etat) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, 'P')""" ,(no_ecr,no_lecr, imput, mnt, lsens, val_ex, val_struct, v_dte))


                                self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecr,no_lecr,val_ex,val_struct))

                            self.env.cr.execute("UPDATE compta_guichet_line SET fg_etat = 'V' where guichet_id = %s and company_id = %s and x_exercice_id = %s and id = %s",(v_id, val_struct, val_ex, ids))
    
    def fermer_caisse(self):
        
        val_ex = int(self.user_id.x_exercice_id)
        val_struct = int(self.company_id)
        val_dte = str(self.dte_jour)
        v_id = int(self.user_id)
        
        self.env.cr.execute("select count(cd_us_caisse)from compta_caisse_struct where fg_resp = True and cd_us_caisse = %s and company_id = %s" ,(v_id, val_struct))
        resul= self.env.cr.fetchone()
        re = resul and resul[0] or 0
        if re == 0:
            raise ValidationError(_('Cette opération est réservée au principal'))
        
        self.env.cr.execute("select * from compta_jour_guichet where dt_ouvert = %s and state = 'O' and company_id = %s", (val_dte, val_struct))
        resultat = self.env.cr.fetchone()
        res = resultat and resultat[0] or 0
        
        if res > 0:
            raise ValidationError(_('Oups!!! Tous les guichets ne sont pas fermés. Cliquez sur le boutton Fermer guichets non fermés'))
        
        
        self.generer_ecr_guichet()
        
        somme = self.mnt_fermeture
        
        self.env.cr.execute("""UPDATE compta_jour_caisse SET dt_fermeture = %s, mnt_fermeture = %s WHERE dt_ouvert = %s and company_id = %s""", (val_dte, somme, val_dte,val_struct))
        
        self.write({'etat': 'F'})
        

class ComptaFermeCaisseLine(models.Model):
    _name = 'compta_ferme_caisse_line'
    
    ferme_caisse_id = fields.Many2one('compta_ferme_caisse', ondelete ='cascade')
    cd_us_guichet = fields.Char("Code guichetier")
    nom_guichetier = fields.Many2one("res.users","Nom guichetier")
    ferme = fields.Char('Etat')
    no_ecr = fields.Integer()
    no_lecr = fields.Integer()
    typ_pj = fields.Integer()
    dte_op = fields.Date()
    fg_sens = fields.Char()
    fg_etat = fields.Char()
    id_imput = fields.Integer()
    var_jr = fields.Integer()
    var_lecr = fields.Integer()
    compte = fields.Integer()
    solde_guichet = fields.Integer('Solde guichet')
    mt_ouverture = fields.Integer('Mnt ouverture')
    totalencaisse = fields.Integer('Total encaissé')
    totaldecaisse = fields.Integer('Total décaissé')
    mntreverse = fields.Integer('Montant reversé')
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    
class ComptaFermeGuichet(models.Model):
    _name = 'compta_ferme_guichet'
    _rec_name = 'guichetier'
    
    guichetier = fields.Many2one("compta_caisse_struct",domain="[('cd_us_caisse','=', user_id)]", string="Guichetier", required=True )
    user_id = fields.Many2one('res.users', string='Caissier', default=lambda self: self.env.user)
    mnt = fields.Integer("Montant", readonly=True)
    dte_jour = fields.Date(default=fields.Date.context_today)
    no_jour = fields.Integer()
    solde = fields.Integer("Solde des opérations (numéraires)", readonly=True)
    cumul_recu = fields.Integer("Cumuls des fonds reçus", readonly=True)
    cumul_remi = fields.Integer("Cumuls des fonds remis", readonly=True)
    mnt_fermeture = fields.Integer("Montant à la fermeture", readonly=True)
    ferme_guichet_line = fields.One2many('compta_ferme_guichet_line', 'ferme_guichet_id', readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('F', 'Guichet fermé')
        ], default='draft', string='Etat')
    
    
    def action_afficher(self):
        
        v_ex = int(self.user_id.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_dte = self.dte_jour
        v_id = int(self.guichetier.cd_us_caisse)
        
        
        self.env.cr.execute("""select no_jour as jour from compta_jour_guichet where dt_ouvert = %s and company_id = %s and cd_us_gui = %s""", (v_dte, val_struct, v_id))
        jr = self.env.cr.fetchone()
        self.no_jour = jr and jr[0] or 0
        v_jr = self.no_jour

        for vals in self:
            vals.env.cr.execute(""" select l.type1 as cat,l.type2 as typ2, l.pj as piece, l.ref_pj as refe, u.mode_reglement as reg, u.nom_usager as nom, l.id_imput as compte,l.x_exercice_id as exo,
            case when u.type_operation = 1 then l.mnt_op_cpta end as encaisse,case when u.type_operation = 2 then l.mnt_op_cpta end as decaisse
            from compta_guichet_line l, compta_guichet_unique u
            where u.id = l.guichet_id and l.x_exercice_id = %s and l.company_id = %s and u.no_jour = %s and u.gui_us = %s and l.fg_etat <> 'A'
            """ ,(val_ex, val_struct, v_jr, v_id))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.ferme_guichet_line.unlink()
            for line in rows:
                result.append((0,0, {'categop' : line['cat'], 'typeop': line['typ2'], 'typepiece': line['piece'], 'refp': line['refe'],'modreg': line['reg'],'intervenant': line['nom'], 'annee': line['exo'], 'mt_encaisse': line['encaisse'], 'mt_decaisse': line['decaisse']}))
            self.ferme_guichet_line = result
            
            
        
        self.env.cr.execute("""select sum(case when gu.type_operation = 1 then l.mnt_op_cpta end) as encaisse
        from compta_guichet_line l, compta_guichet_unique gu
        where l.x_exercice_id = %s and l.company_id = %s and gu.gui_us = %s and gu.id = l.guichet_id 
        and gu.no_jour = %s and l.fg_etat <> 'A'""", (val_ex, val_struct,v_id,v_jr ))
        cr = self.env.cr.fetchone()
        crecu = cr and cr[0] or 0
        
        self.env.cr.execute("""select mnt_ouverture from compta_jour_guichet where dt_ouvert = %s and no_jour = %s and cd_us_gui = %s
        and company_id = %s and x_exercice_id = %s""",(v_dte, v_jr,v_id,val_struct,val_ex))
        ouver = self.env.cr.fetchone()
        ouvert = ouver and ouver[0] or 0
        
        self.cumul_recu = ouvert + crecu
        
        self.env.cr.execute("""select sum(case when gu.type_operation = 2 then l.mnt_op_cpta end) as decaisse
        from compta_guichet_line l, compta_guichet_unique gu
        where gu.id = l.guichet_id and l.x_exercice_id = %s and l.company_id = %s and gu.gui_us = %s and gu.no_jour = %s and l.fg_etat <> 'A' """, (val_ex, val_struct, v_id, v_jr))
        ce = self.env.cr.fetchone()
        cemis = ce and ce[0] or 0 
        self.cumul_remi = cemis 
        
        self.mnt_fermeture = self.cumul_recu - self.cumul_remi

        
        self.env.cr.execute("""select sum(l.mnt_op_cpta)
        from compta_guichet_line l, compta_guichet_unique gu where gu.id = l.guichet_id and l.x_exercice_id = %s and l.company_id = %s
        and gu.gui_us = %s and gu.no_jour = %s and modreg='0' and l.fg_etat <> 'A' """ ,(val_ex, val_struct, v_id, v_jr))
        sol = self.env.cr.fetchone()
        self.solde = sol and sol[0] or 0 
    
    def fermer_guichet(self):
        
        val_ex = int(self.user_id.x_exercice_id)
        val_struct = int(self.company_id)
        v_date = self.dte_jour
        v_jr = int(self.no_jour)
        v_mntfermeture = int(self.mnt_fermeture)
        v_id = int(self.guichetier.cd_us_caisse)

        self.env.cr.execute("""UPDATE compta_jour_guichet SET state = 'F', dt_fermeture = %s, mnt_fermeture = %s WHERE x_exercice_id = %s and company_id = %s and no_jour = %s and cd_us_gui = %s""" ,(v_date,v_mntfermeture, val_ex, val_struct, v_jr, v_id))
        
        self.write({'state': 'F'})
    
class ComptaFermeGuichetLine(models.Model):
    _name = 'compta_ferme_guichet_line'
    
    ferme_guichet_id = fields.Many2one('compta_ferme_guichet', ondelete ='cascade')
    categop = fields.Many2one("compta_operation_guichet","Catégorie opération")
    typeop = fields.Many2one("compta_type_op_cpta","Type opération")
    natdet = fields.Char('Nature détaillée')
    compte = fields.Many2one('ref_souscompte', "Compte")
    intervenant = fields.Char("Intervenant extérieur")
    modreg = fields.Many2one("compta_jr_modreg", "Mode Reg")
    typepiece = fields.Many2one("compta_piece_line","Type de pièce")
    refp = fields.Char('Référence pièce')
    annee = fields.Many2one("ref_exercice",'Année')
    mt_encaisse = fields.Integer('Montant encaissé')
    mt_decaisse = fields.Integer('Montant décaissé')
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
  
    

class ComptaCompteurGuichet(models.Model):
    _name = 'compta_compteur_guichet'
    
    numop = fields.Integer(default=0)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaMontant(models.Model):
    _name = 'compta_montant'
    _rec_name = 'montant'
    
    montant = fields.Integer('Libelle')
    

class ComptaBilletage(models.Model):
    _name = 'compta_billetage'
    
    name = fields.Char("Nom", default="Billetage")
    no_jour = fields.Integer('N° Jour', readonly=True)
    mnt = fields.Float('Montant fermeture',readonly=True)
    dte_jour = fields.Date(default=fields.Date.context_today,readonly=False)
    guichetier = fields.Many2one("compta_caisse_struct",domain="[('cd_us_caisse','=', user_id)]", string="Guichetier", required=True, states={'V': [('readonly', True)]} )
    user_id = fields.Many2one('res.users', string='Caissier', default=lambda self: self.env.user)
    billetage_line = fields.One2many('compta_billetage_line', 'billetage_id', states={'V': [('readonly', True)]})
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('V', 'Billetage effectué'),
        ], default='draft')
    
    
    @api.multi
    def action_valider(self):
        
        val_ex = int(self.user_id.x_exercice_id)
        val_struct = int(self.company_id)
        vr_dte = self.dte_jour
        v_id = int(self.guichetier.cd_us_caisse)
        v1_id = int(self.guichetier)
        val_id = int(self.id)
        v_jr = int(self.no_jour)
        
        self.env.cr.execute("select count(cd_us_caisse) from compta_caisse_struct where company_id = %d and cd_us_caisse = %d" %(val_struct, v_id))
        res = self.env.cr.fetchone()
        res1 = res and res[0] or 0
        if res1 != 1:
            raise ValidationError(_("Vous n'êtes pas guichetier. Vous ne pouver donc pas effectuer cette opération."))
        
            
        self.env.cr.execute("select mnt from compta_billetage where no_jour = %d and guichetier = %d and company_id = %d and x_exercice_id = %d" %(v_jr, v1_id, val_struct, val_ex))
        mont = self.env.cr.fetchone()
        montant = mont and mont[0] or 0
        
        self.env.cr.execute("select sum(mnt) from compta_billetage_line where billetage_id = %d and company_id = %d and x_exercice_id = %d" %(val_id,val_struct, val_ex))
        tot = self.env.cr.fetchone()
        total = tot and tot[0] or 0
        
        if total != montant:
            raise ValidationError(_("Le montant total du billetage est différent du montant à la fermeture de votre guichet."))
        
        self.write({'state': 'V'})
    
    @api.onchange('dte_jour')
    def initialiser(self):
        
        val_ex = int(self.user_id.x_exercice_id)
        val_struct = int(self.company_id)
        vr_dte = str(self.dte_jour)
        #v_id = int(self.guichetier.cd_us_caisse)
        
        self.env.cr.execute("select no_jour, cd_us_caisse, dt_ouvert from compta_jour_caisse where dt_ouvert = '%s' and x_exercice_id = %s " %(vr_dte, val_ex))
        num = self.env.cr.dictfetchall()
        numero  = num and num[0]["no_jour"]
        dte = num and num[0]["dt_ouvert"]
        dte1 = str(dte)
        v_id = num and num[0]["cd_us_caisse"]
        self.guichetier = v_id
        
        if dte1 != vr_dte:
            raise ValidationError(_('Vous ne pouvez pas effectuer le billetage pour ce jour.'))
        else:
            self.no_jour = numero
            v_jr = self.no_jour
            
            self.env.cr.execute("""select sum( case when u.type_operation = 1 then l.mnt_op_cpta end) - coalesce(sum( case when u.type_operation = 2 then l.mnt_op_cpta end),0) as encours
            from compta_guichet_line l, compta_guichet_unique u where u.id = l.guichet_id and u.no_jour = %s
            and l.company_id = %s and l.x_exercice_id = %s and u.gui_us = %s and modreg = '0' and l.fg_etat <> 'A' """ ,(v_jr, val_struct, val_ex, v_id))
            mt = self.env.cr.fetchone()
            self.mnt = mt and mt[0] or 0
            

class ComptaBilletageLine(models.Model):
    _name = 'compta_billetage_line'
    
    billetage_id = fields.Many2one('compta_billetage', ondelete='cascade')
    libelle = fields.Many2one('compta_montant', 'Libellé')
    qte = fields.Integer('Quantité')
    mnt = fields.Float('Montant')
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
   
    
    @api.onchange('qte','libelle')
    def calcul(self):
        for x in self:
            x.mnt = x.libelle.montant * x.qte


class Test(models.Model):
    
    _name = "testok"
    _auto = False
   
    
    @api.model
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, 'testok')
        self.env.cr.execute("""CREATE OR REPLACE VIEW testok AS
            SELECT 
            id, lb_long
            FROM 
            budg_rubrique """)


            
"""
#class pour creer la vue sur le model budg_rubrique
class VueNature(models.Model):
    
    _name = "vue_nature"
    _auto = False
 
    
    @api.model
    def init(self):
        
        tools.drop_view_if_exists(self.env.cr, 'vue_nature')
        self.env.cr.execute(" CREATE OR REPLACE VIEW vue_nature AS (
            SELECT 
                ru.id cd_nat,
                r.rubrique lb_nat, ru.cd_rubrique vl_nat, a.cd_article,
                t.cd_titre, s.cd_section, c.cd_chapitre, p.cd_paragraphe, f.no_ex, rc.code_struct
            FROM 
                budg_rubrique r, budg_article a, budg_chapitre c, budg_section s, budg_paragraphe p, 
                budg_titre t, ref_exercice f, res_company rc, ref_rubrique ru
            WHERE 
                r.cd_titre_id = t.id and r.cd_section_id = s.id and r.cd_chapitre_id = c.id and 
                r.cd_article_id = a.id and r.cd_paragraphe_id = p.id 
                and f.id = r.x_exercice_id and rc.id = r.company_id
                and r.x_exercice_id = 1 and r.company_id = 1 
        ))
"""

class ComptaQuittanceUnique(models.Model):
    
    _name = 'compta_quittance_unique'
    _rec_name = 'no_quittance'
    
    no_op = fields.Many2one("compta_guichet_unique", string="N° opération")
    no_quittance = fields.Char("N° quittance", readonly=True)
    type_quittance_id = fields.Many2one("compta_type_quittance",readonly=True   )
    nom_intervenant = fields.Char("Intervenant", readonly=True)
    tel_benef = fields.Char("Téléphone",readonly=True)
    dte_jour = fields.Date(default=fields.Date.context_today,readonly=False)
    telephone = fields.Char("Téléphone")
    mode_reg = fields.Char("Mode de règlement", readonly=True)
    mnt_op_gui = fields.Integer("Montant payé", readonly=True)
    mnt_recu = fields.Integer("Montant dû", required=True)
    numero = fields.Char("Réf. Chèque", readonly=True)
    mnt_rests = fields.Integer("Reste à payer", compute='_mnt_restant', store=True)
    mnt_rest = fields.Integer()
    facture = fields.Char("Facture", readonly=False)
    facture_id = fields.Char("Facture", readonly=False)
    state = fields.Selection([
        ('V', 'Validé'),
        ('A', 'Annulé')], 'Etat')
    objet = fields.Text("Objet")
    dte_f = fields.Date("Date Fac.")
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    us = fields.Many2one("compta_caisse_struct",default=lambda self: self.env['compta_caisse_struct'].search([('fg_resp','=', True)]), readonly= True, string="Nom guichetier")
    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
    guichet = fields.Many2one('res.users', string='Guichetier', default=lambda self: self.env.user)
    operation_line = fields.One2many('listenature','guichet_id')
    
    
    def Nature(self):
        
        val_ex = int(self.no_op.x_exercice_id)
        val_struct = int(self.company_id)
        val_bq = int(self.no_op)
        
        for vals in self:
            vals.env.cr.execute("""select type1, type2, id_tlv, mnt_op_cpta as mnt
            from compta_guichet_line r where x_exercice_id = %s and company_id = %s and guichet_id = %s""" ,(val_ex, val_struct, val_bq))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.operation_line.unlink()
            for line in rows:
                result.append((0,0, {'type1' : line['type1'], 'type2': line['type2'], 'id_tlv': line['id_tlv'], 'mnt_actuel': line['mnt']}))
            self.operation_line = result
    
    
    @api.onchange('no_op')
    def no_op_on_change(self):

        if self.no_op:
            self.mnt_op_gui = self.no_op.mnt_total
            self.nom_intervenant = self.no_op.nom_usager
            self.mode_reg = self.no_op.mode_reglement.name.lb_long
            self.facture = self.no_op.factures
            self.facture_id = self.no_op.facture.num_facture
            self.dte_f = self.no_op.dte_f
            self.type_quittance_id = self.no_op.type_quittance
            self.tel_benef = self.no_op.contact 
            self.numero = self.no_op.numero
            self.x_exercice_id = self.no_op.x_exercice_id



    @api.depends('mnt_op_gui','mnt_recu')
    def _mnt_restant(self):
        for x in self:
            x.mnt_rests = x.mnt_recu - x.mnt_op_gui         

    @api.depends('mnt_op_gui')
    def amount_to_words(self):
        self.text_amount = num2words(self.mnt_op_gui, lang='fr')



    @api.multi
    def action_valider(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select noquittance from compta_compteur_quittance_unique where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        quittance = self.env.cr.fetchone()
        no_quittance = quittance and quittance[0] or 0
        c1 = int(no_quittance) + 1
        c = str(no_quittance)
        if c == "0":
            ok = str(c1).zfill(4)
            self.no_quittance = ok
            vals = c1
            self.env.cr.execute("""INSERT INTO compta_compteur_quittance_unique(x_exercice_id,company_id,noquittance)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))    
            self.write({'state': 'V'})
        else:
            c1 = int(no_quittance) + 1
            c = str(no_quittance)
            ok = str(c1).zfill(4)
            self.no_quittance = ok
            vals = c1
            self.env.cr.execute("UPDATE compta_compteur_quittance_unique SET noquittance = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))
            self.write({'state': 'V'})
        
    
    @api.multi
    def action_annuler(self):
        self.write({'state': 'A'})


class Listenature(models.Model):
    _name = "listenature"
    
    guichet_id = fields.Many2one("compta_quittance_unique", ondelete='cascade')
    type1 = fields.Many2one("compta_operation_guichet", "Catérogie")
    type2 = fields.Many2one("compta_type_op_cpta", "Nature opération" )
    id_tlv = fields.Many2one("compta_table_listnat", "Nature détaillée" )
    mnt_actuel = fields.Float("Montant", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)        
class Compta_cheque_rec(models.Model):
    _name = "compta_cheque_rec"
    _rec_name = "no_op"
    
    no_op = fields.Many2one("compta_guichet_unique", string="N° opération",domain=[('state', '=', 'C')])
    cd_bq_emis = fields.Many2one("res.bank", 'Banque', required=True, states={'C': [('readonly', True)]})
    no_agence = fields.Many2one("compta_comptebanque", 'Agence', required=True, states={'C': [('readonly', True)]})
    no_cheq_emis = fields.Char("Référence du chèque", required=True, states={'C': [('readonly', True)]})
    no_ivext_emis = fields.Char("Emis par", required=True, states={'C': [('readonly', True)]})
    dt_recu = fields.Date("Reçu le", required=True, states={'C': [('readonly', True)]})
    dt_emis = fields.Date("Emis le", required=True, states={'C': [('readonly', True)]})
    mnt_cheq_rec = fields.Integer("Montant du chèque", required=True, states={'C': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('V', 'Validé'),
        ], default='draft', string="Etat")
    
    @api.multi
    def action_valider(self):
        self.write({'state': 'V'})

class Compta_compteur_quittance_unique(models.Model):
    
    _name = "compta_compteur_quittance_unique"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    noquittance = fields.Integer()
    
class ComptaChequeRecu(models.Model):
    _name = 'compta_cheque_recu'
    _rec_name = 'num_cheque'
    
    banque_id = fields.Many2one("res.bank", "Banque", required=True)
    agence_id = fields.Many2one("ref_banque_agence", "Agence", required=True)
    num_cheque = fields.Char("N° chèque", required=True)
    dt_cheque_emis = fields.Date("Date émission", required=True)
    dt_cheque_recu = fields.Date("Date réception", required=True)
    nom_emeteur = fields.Char("Nom de l'émetteur", required=True)
    montant = fields.Float("Montant", required=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Nouveau'),
        ('P', 'Mis en portefeuille'),
        ('E', 'Encaissé')
        ], default='draft', string="Etat", required=True)
    
    def VerifCheqUniq(self):
        
        v_num = self.num_cheque
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_banq = int(self.banque_id)
        self.env.cr.execute("""SELECT count(id) FROM compte_cheque_recu where num_cheque = %s and 
        company_id = %s and x_exercice_id = %s and banque_id = %s """ ,(v_num, v_ex, v_struct, v_banq))
        
        res = self.env.cr.fetchone()
        val = res and res[0] or 0
        if val > 1:
            raise ValidationError(_('Erreur un chèque enregistré sous numéro a été déja enregistré pour cette banque. Veuillez corriger !'))
        
        self.write({'state': 'N'})


class ComptaPortefeuille(models.Model):
    _name = 'compta_portefeuille'
    _rec_name = 'banque_id'
    
    banque_id = fields.Many2one("res.bank", "Banque", required=True)
    total = fields.Integer("Total", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    portefeuille_ids = fields.One2many("compta_portefeuille_line", "portefeuille_id")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Nouveau'),
        ('V', 'Validé'),
        ], default='draft', string="Etat")
    
    
    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_bq = int(self.banque_id)
        
        for vals in self:
            vals.env.cr.execute("""select r.agence_id as agence, r.num_cheque as refe, r.dt_cheque_emis as dte, r.montant as mnt,r.nom_emeteur as emet
            from compta_cheque_recu r where x_exercice_id = %s and company_id = %s and banque_id = %s and r.state = 'N'""" ,(val_ex, val_struct, val_bq))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.portefeuille_ids.unlink()
            for line in rows:
                result.append((0,0, {'agence' : line['agence'], 'ref_cheq': line['refe'], 'dt_effet': line['dte'], 'montant': line['mnt'], 'emetteur': line['emet']}))
            self.portefeuille_ids = result
    
    
    def valider(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_id = int(self.id)
        
        self.env.cr.execute("""select sum(montant) from compta_portefeuille_line where portefeuille_id = %d and company_id = %d and x_exercice_id = %d""" %(val_id, val_struct, val_ex))
        res = self.env.cr.fetchone()
        self.total = res and res[0] or 0
        self.write({'state': 'N'})
    

class ComptaPortefeuilleLine(models.Model):
    _name = "compta_portefeuille_line"
    
    portefeuille_id = fields.Many2one("compta_portefeuille", ondelete='cascade')
    agence = fields.Many2one("ref_banque_agence", "Agence", readonly=True)
    ref_cheq = fields.Char("Réf. Chèque", readonly=True)
    dt_effet = fields.Date("Date effet", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    emetteur = fields.Char("Emetteur")
    cocher = fields.Boolean("Cocher pr Portf")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
class ComptaEncaissement(models.Model):
    _name = 'compta_encaissement'
    _rec_name = 'banque_id'
    
    banque_id = fields.Many2one("compta_portefeuille", "Banque",domain=[('state', '=', 'N')], required=True)
    total = fields.Float("Total", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    encaissement_ids = fields.One2many("compta_encaissement_line", "encaissement_id")
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Nouveau'),
        ('T', 'Traité'),
        ], default='draft', string="Etat")
    
    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_bq = int(self.banque_id)
        
        for vals in self:
            vals.env.cr.execute("""select r.agence as agence, r.ref_cheq as refe, r.dt_effet as dte, r.montant as mnt, r.emetteur as emet
            from compta_portefeuille_line r where x_exercice_id = %s and company_id = %s and portefeuille_id = %s and cocher = True""" ,(val_ex, val_struct, val_bq))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.encaissement_ids.unlink()
            for line in rows:
                result.append((0,0, {'agence' : line['agence'], 'ref_cheq': line['refe'], 'dt_effet': line['dte'], 'montant': line['mnt'], 'emetteur': line['emet']}))
            self.encaissement_ids = result
            
    def valider(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_bq = int(self.banque_id)
        
        self.env.cr.execute("UPDATE compta_portefeuille SET state = 'V' WHERE id = %d and x_exercice_id = %d and company_id = %d" %(val_bq,val_ex,val_struct))
    

class ComptaEncaissementLine(models.Model):
    _name = "compta_encaissement_line"
    
    encaissement_id = fields.Many2one("compta_encaissement", ondelete='cascade')
    agence = fields.Many2one("ref_banque_agence", "Agence", readonly=True)
    ref_cheq = fields.Char("Numéro Chèque", readonly=True)
    dt_effet = fields.Date("Reçu le", readonly=True)
    emetteur = fields.Char("Emis par", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    encaisser = fields.Boolean("Encaissé ?")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
  

class ComptaSuiviEncaissement(models.Model):
    _name = "compta_suivi_encaissement"
    
    name = fields.Char("nom", default="Encaissement chèque")
    total_cheque_encaisser = fields.Float("Total chèque à encaisser", readonly=True)
    nbre = fields.Integer("Nombre de chèque", readonly=True)
    total_cheque_hors_encaisser = fields.Float("Total chèque hors encaisser", readonly=True)
    no_ecr = fields.Integer()
    type_journal = fields.Many2one("compta_type_journal",default=lambda self: self.env['compta_type_journal'].search([('type_journal','=', 'JB')]))
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture', default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'B')]))
    dte = fields.Date("Date", default=fields.Date.context_today, readonly=True)
    suivi_ids = fields.One2many("compta_suivi_encaissement_line", "suivi_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Nouveau'),
        ('T', 'Traité'),
        ], default='draft', string="Etat")
    
    
    def afficher(self):
    
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("""select count(*) as nbre, sum(montant) as somme
        from compta_encaissement_line r where x_exercice_id = %d and company_id = %d and r.encaisser = True""" %(val_ex, val_struct))
        res = self.env.cr.dictfetchall()
        self.total_cheque_encaisser = res and res[0]['somme']
        self.nbre = res and res[0]['nbre']
        
        
        for vals in self:
            vals.env.cr.execute("""select r.agence as agence, r.ref_cheq as refe, r.dt_effet as dte, r.montant as mnt, r.emetteur as emet,r.encaisser as encaisser
            from compta_encaissement_line r where x_exercice_id = %s and company_id = %s and r.encaisser = True""" ,(val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.suivi_ids.unlink()
            for line in rows:
                result.append((0,0, {'agence' : line['agence'], 'ref_cheq': line['refe'], 'dt_effet': line['dte'], 'montant': line['mnt'], 'emetteur': line['emet'], 'encaisser': line['encaisser']}))
            self.suivi_ids = result
    
    @api.multi
    def gen_ecr_enc(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
        id_enc = int(self.id)
        val_date = self.dte
       
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.suivi_ids:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            no_ecrs11 = no_ecrs1 + 1
            no_ecrs1= no_ecrs11
            for record in self.suivi_ids:           
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
        for record in self.suivi_ids:
            val = (self.no_ecr)
            val_id = (self.id)
            self.env.cr.execute("UPDATE compta_suivi_encaissement_line SET no_ecr = %s WHERE suivi_id = %s", (val, val_id))
        
        self.env.cr.execute("select * from compta_suivi_encaissement where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_enc))
        curs_paiement = self.env.cr.dictfetchall()
        no_ecrs = curs_paiement and curs_paiement[0]['no_ecr']
        no_ecr = int(no_ecrs)
        typ_jr = curs_paiement and curs_paiement[0]['type_journal']
        typ_ecr = curs_paiement and curs_paiement[0]['type_ecriture']
        
        
        self.env.cr.execute("""select * from compta_regle_operation_banque u, compta_type_op_banque b
        where u.code = 'BR1' and u.id = b.regle_id and b.type_opbq = '12' and u.x_exercice_id = %d and u.company_id = %d""" %(val_ex,val_struct))
        compte = self.env.cr.dictfetchall()
        credit = compte and compte[0]['cred_id']
        debit = compte and compte[0]['deb_id']
        
        
        self.env.cr.execute("INSERT INTO compta_ecriture(dt_ecriture,no_ecr,type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BR', %s, %s, 'P')" ,(val_date,no_ecr, typ_ecr, typ_jr, val_ex, val_struct))

        self.env.cr.execute("select * from compta_suivi_encaissement_line where x_exercice_id = %d and company_id = %d and suivi_id = %d " %(val_ex,val_struct, id_enc))
        curs_cheq_dep = self.env.cr.dictfetchall()
        var_ecr = self.no_ecr
        
        for val in self.suivi_ids:
            vl_mnt = val.montant
            no_ecrs11 = no_ecrs11 + 1
            
            if val.encaisser == True:
        
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id,dt_ligne, fg_sens, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'C', 'P') """ ,(var_ecr,no_ecrs11, credit, vl_mnt,val_ex, val_struct, val_date))
                
                no_ecrs11 = no_ecrs11 + 1
                no_ecrs12 = no_ecrs11
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id,dt_ligne, fg_sens, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'D', 'P') """ ,(var_ecr,no_ecrs12, debit, vl_mnt,val_ex, val_struct, val_date))
        
        self.env.cr.execute("UPDATE compta_compteur_ecr SET no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecrs12,val_ex,val_struct))
            
        self.write({'state': 'N'})    


class ComptaSuiviEncaissementLine(models.Model):
    _name = "compta_suivi_encaissement_line"
    
    no_ecr = fields.Integer()
    no_lecr = fields.Integer()
    suivi_id = fields.Many2one('compta_suivi_encaissement', ondelete='cascade')
    agence = fields.Many2one("ref_banque_agence", "Agence", readonly=True)
    ref_cheq = fields.Char("Numéro Chèque", readonly=True)
    dt_effet = fields.Date("Reçu le", readonly=True)
    emetteur = fields.Char("Emis par", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    encaisser = fields.Boolean("")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaSuiviRejet(models.Model):
    _name = "compta_suivi_rejet"
    
    total_cheque_encaisser = fields.Float("Encaissé", readonly=True)
    nbre = fields.Integer("Nombre de chèque", readonly=True)
    total_cheque_rejeter = fields.Float("Rejetés", readonly=True)
    no_ecr = fields.Integer()
    type_journal = fields.Many2one("compta_type_journal",default=lambda self: self.env['compta_type_journal'].search([('type_journal','=', 'JB')]))
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture', default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'X')]))
    dte = fields.Date("Date", default=fields.Date.context_today, readonly=True)
    suivi_ids = fields.One2many("compta_suivi_rejet_line", "suivi_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Nouveau'),
        ('T', 'Traité'),
        ], default='draft', string="Etat") 
    
    
    def afficher(self):
    
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("""select count(*) as nbre, sum(montant) as somme
        from compta_encaissement_line r where x_exercice_id = %d and company_id = %d and r.encaisser = False""" %(val_ex, val_struct))
        res = self.env.cr.dictfetchall()
        self.total_cheque_encaisser = res and res[0]['somme']
        self.nbre = res and res[0]['nbre']
        
        
        for vals in self:
            vals.env.cr.execute("""select r.agence as agence, r.ref_cheq as refe, r.dt_effet as dte, r.montant as mnt, r.emetteur as emet,r.encaisser as encaisser
            from compta_encaissement_line r where x_exercice_id = %s and company_id = %s and r.encaisser = False""" ,(val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.suivi_ids.unlink()
            for line in rows:
                result.append((0,0, {'agence' : line['agence'], 'ref_cheq': line['refe'], 'dt_effet': line['dte'], 'montant': line['mnt'], 'emetteur': line['emet'], 'encaisser': line['encaisser']}))
            self.suivi_ids = result
    
    @api.multi
    def gen_ecr_enc(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
        id_enc = int(self.id)
        val_date = self.dte
       
        if not(no_ecr):           
            self.no_ecr = 1
            no_ecrs1 = 0
            for record in self.suivi_ids:
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("""INSERT INTO compta_compteur_ecr(x_exercice_id,company_id,no_ecr,no_lecr) VALUES(%d, %d, %d, %d)""" %(val_struct,val_ex,self.no_ecr, record.no_lecr))
        else:
            self.no_ecr = no_ecr + 1
            no_ecrs11 = no_ecrs1 + 1
            no_ecrs1= no_ecrs11
            for record in self.suivi_ids:           
                no_ecrs1 = no_ecrs1 + 1
                record.no_lecr = no_ecrs1 
            self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %d, no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(self.no_ecr,record.no_lecr,val_ex,val_struct))
        
        for record in self.suivi_ids:
            val = (self.no_ecr)
            val_id = (self.id)
            self.env.cr.execute("UPDATE compta_suivi_rejet_line SET no_ecr = %s WHERE suivi_id = %s", (val, val_id))
        
        self.env.cr.execute("select * from compta_suivi_rejet where x_exercice_id = %d and company_id = %d and id = %d" %(val_ex,val_struct, id_enc))
        curs_paiement = self.env.cr.dictfetchall()
        no_ecrs = curs_paiement and curs_paiement[0]['no_ecr']
        no_ecr = int(no_ecrs)
        typ_jr = curs_paiement and curs_paiement[0]['type_journal']
        typ_ecr = curs_paiement and curs_paiement[0]['type_ecriture']
        
        self.env.cr.execute("""select * from compta_regle_operation_banque u, compta_type_op_banque b
        where u.code = 'BR9' and u.id = b.regle_id and b.type_opbq = '01' and u.x_exercice_id = %d and u.company_id = %d""" %(val_ex,val_struct))
       
        compte = self.env.cr.dictfetchall()
        credit = compte and compte[0]['cred_id']
        debit = compte and compte[0]['deb_id']
        
        
        self.env.cr.execute("INSERT INTO compta_ecriture(dt_ecriture,no_ecr,type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'BR', %s, %s, 'P')" ,(val_date,no_ecr, typ_ecr, typ_jr, val_ex, val_struct))

        self.env.cr.execute("select * from compta_suivi_rejet_line where x_exercice_id = %d and company_id = %d and suivi_id = %d " %(val_ex,val_struct, id_enc))
        curs_cheq_dep = self.env.cr.dictfetchall()
        var_ecr = self.no_ecr
        
        for val in self.suivi_ids:
            vl_mnt = val.montant
            no_ecrs11 = no_ecrs11 + 1
            
            if val.rejet == True:
        
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id,dt_ligne, fg_sens, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'C', 'P') """ ,(var_ecr,no_ecrs11, credit, vl_mnt,val_ex, val_struct, val_date))
                
                no_ecrs11 = no_ecrs11 + 1
                no_ecrs12 = no_ecrs11
                self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id,dt_ligne, fg_sens, fg_etat) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'D', 'P') """ ,(var_ecr,no_ecrs12, debit, vl_mnt,val_ex, val_struct, val_date))
        
        self.env.cr.execute("UPDATE compta_compteur_ecr SET no_lecr = %d WHERE x_exercice_id = %d and company_id = %d" %(no_ecrs12,val_ex,val_struct))
            
        self.write({'state': 'N'})    



class ComptaSuiviRejetLine(models.Model):
    _name = "compta_suivi_rejet_line"
    
    no_ecr = fields.Integer()
    no_lecr = fields.Integer()
    suivi_id = fields.Many2one('compta_suivi_rejet', ondelete='cascade')
    agence = fields.Many2one("ref_banque_agence", "Agence", readonly=True)
    ref_cheq = fields.Char("Numéro Chèque", readonly=True)
    dt_effet = fields.Date("Reçu le", readonly=True)
    emetteur = fields.Char("Emis par", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    rejet = fields.Boolean("Rejet ?", default=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaParamModeReg(models.Model):
    _name = "compta_param_mode_regul"
    _rec_name = "mode_id"
    
    mode_id = fields.Many2one("compta_mode_regularisation", "Mode de regularisation", required=True)
    imputation = fields.Many2one("compta_plan_line", "Imputation", required=True)
    piece_id = fields.Many2one("ref_piece_justificatives", "Type de PJ", required=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    


class ComptaRegularisation(models.Model):
    _name = "compta_regularisation"
    _rec_name = "mode_id"
    
    mode_id = fields.Many2one("compta_param_mode_regul", "Mode de régularisation", required=True)
    cpte = fields.Many2one("compta_plan_line","Compte de débit", readonly=True)
    cpte_deb = fields.Integer()
    total_rejet = fields.Float("Total/Rejet", readonly=True)
    total_regul = fields.Float("Total/Regul", readonly=True)
    piece = fields.Many2one("ref_piece_justificatives", "Pièce justificative", readonly=True)
    regularisation_lines = fields.One2many("compta_regularisation_line", "regularisation_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    @api.onchange('mode_id')
    def OnchangeMode(self):
        if self.mode_id:
            self.cpte = self.mode_id.imputation
            self.cpte_deb = self.mode_id.imputation.souscpte.id
            self.piece = self.mode_id.piece
            
    
    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        for vals in self:
            vals.env.cr.execute("""select r.agence as agence, r.ref_cheq as refe, r.dt_effet as dte, r.montant as mnt, r.emetteur as emet
            from compta_encaissement_line r where x_exercice_id = %s and company_id = %s and r.encaisser = False""" ,(val_ex, val_struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.regularisation_lines.unlink()
            for line in rows:
                result.append((0,0, {'agence' : line['agence'], 'ref_cheq': line['refe'], 'dt_effet': line['dte'], 'montant': line['mnt'], 'emetteur': line['emet'], 'encaisser': line['encaisser']}))
            self.regularisation_lines = result
        

class ComptaRegularisationLine(models.Model):
    _name = "compta_regularisation_line"
    
    regularisation_id = fields.Many2one("compta_regularisation", ondelete='cascade')
    banque_id = fields.Many2one('res.bank', "Banque", readonly=True)
    agence = fields.Many2one("ref_banque_agence", "Agence", readonly=True)
    ref_cheq = fields.Char("Numéro Chèque", readonly=True)
    dt_effet = fields.Date("Date effet le", readonly=True)
    montant = fields.Float("Montant", readonly=True)
    montant_reg = fields.Float("Montant à régulariser")
    penalite = fields.Float("Pénalité")
    reg = fields.Boolean("Reg ?", default=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)    



class ComptaJournalRecette(models.Model):
    _name = "compta_journal_recette"
    
    dte_deb = fields.Date("Du", required = True)
    dte_fin = fields.Date("Au", required = True)
    recette_lines = fields.One2many("compta_journal_recette_lines", "recette_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        d_deb = self.dte_deb
        d_fin = self.dte_fin

        for vals in self:
            vals.env.cr.execute("""select distinct bt.lb_objet as nature, l.num_titre as titre, no_bord_rec as bord, date_titre as dte, imp_deb as debit, imp_cred as credit, montant as mntdebit, montant as mntcredit
            from compta_prise_charge_line_rec l, budg_detail_bord_recette bd, budg_bord_titre_recette b, budg_titrerecette bt
            where b.id = bd.budg_bord_titre_recette_id and bd.budg_titrerecette_id = bt.id and l.x_exercice_id = %s and l.company_id = %s and bt.cd_titre_recette = l.num_titre and l.date_titre
            between %s and %s order by titre """ ,(val_ex, val_struct, d_deb, d_fin))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.recette_lines.unlink()
            for line in rows:
                result.append((0,0, {'titre' : line['titre'], 'bord': line['bord'], 'nature': line['nature'], 'dte': line['dte'], 'cpte_deb': line['debit'], 
                'cpte_cred': line['credit'],'mnt_deb': line['mntdebit'],'mnt_cred': line['mntcredit']}))
            self.recette_lines = result



class ComptaJournalRecetteLines(models.Model):
    _name = "compta_journal_recette_lines"
    
    recette_id = fields.Many2one("compta_journal_recette")
    dte = fields.Date("Date")
    titre = fields.Char("N° de Titre")
    bord = fields.Char("N° Bordereau")
    nature = fields.Char("Nature de la recette")
    cpte_deb = fields.Char("Compte Débit")
    cpte_cred = fields.Char("Compte Crébit")
    mnt_deb = fields.Float("Montant Débit")
    mnt_cred = fields.Float("Montant Crébit")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaJournalDepense(models.Model):
    _name = "compta_journal_depense"
    
    name = fields.Char("Journal des dépense")
    dte_deb = fields.Date("Du", required = True)
    dte_fin = fields.Date("Au", required = True)
    depense_lines = fields.One2many("compta_journal_depense_lines", "depense_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        d_deb = self.dte_deb
        d_fin = self.dte_fin

        for vals in self:
            vals.env.cr.execute("""select distinct bm.obj as nature, num_mandat as mdt, no_bord_mandat as bord, date_mandat as dte, imp_deb as debit, imp_cred as credit, montant as mntdebit, montant as mntcredit
            from compta_prise_charge_line l, budg_detail_bord_mandat bd, budg_bordereau_mandatement b, budg_mandat bm
            where b.id = bd.budg_bordereau_mandatement_id and bd.budg_mandat_id = bm.id and bm.no_mandat = l.num_mandat and l.x_exercice_id = %s and l.company_id = %s and l.date_mandat 
            between %s and %s order by mdt """ ,(val_ex, val_struct, d_deb, d_fin))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.depense_lines.unlink()
            for line in rows:
                result.append((0,0, {'mandat' : line['mdt'], 'bord': line['bord'], 'nature': line['nature'], 'dte': line['dte'], 'cpte_deb': line['debit'], 
                'cpte_cred': line['credit'],'mnt_deb': line['mntdebit'],'mnt_cred': line['mntcredit']}))
            self.depense_lines = result

class ComptaJournalDepenseLines(models.Model):
    _name = "compta_journal_depense_lines"
    
    depense_id = fields.Many2one("compta_journal_depense")
    dte = fields.Date("Date")
    mandat = fields.Char("N° de Mandat")
    bord = fields.Char("N° Bordereau")
    nature = fields.Char("Nature de la dépense")
    cpte_deb = fields.Char("Compte Débit")
    cpte_cred = fields.Char("Compte Crébit")
    mnt_deb = fields.Float("Montant Débit")
    mnt_cred = fields.Float("Montant Crébit")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
class ComptaJournalBanque(models.Model):
    _name = "compta_journal_banque"
    
    dte_deb = fields.Date("Du", required = True)
    dte_fin = fields.Date("Au", required = True)
    banque_lines = fields.One2many("compta_journal_banque_lines", "banque_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

class ComptaJournalBanqueLines(models.Model):
    _name = "compta_journal_banque_lines"
    
    banque_id = fields.Many2one("compta_journal_banque")
    dte = fields.Date("Date")
    refpiece = fields.Char("Ref Pièce")
    nature = fields.Char("Nature de l'opération")
    cpte_deb = fields.Char("Compte Débit")
    cpte_cred = fields.Char("Compte Crébit")
    mnt_deb = fields.Float("Montant Débit")
    mnt_cred = fields.Float("Montant Crébit")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaJournalCaisse(models.Model):
    _name = "compta_journal_caisse"
    
    dte_deb = fields.Date("Du", required = True)
    dte_fin = fields.Date("Au", required = True)
    caisse_lines = fields.One2many("compta_journal_caisse_lines", "caisse_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

class ComptaJournalCaisseLines(models.Model):
    _name = "compta_journal_caisse_lines"
    
    caisse_id = fields.Many2one("compta_journal_caisse")
    dte = fields.Date("Date")
    refpiece = fields.Char("Ref Pièce")
    nature = fields.Char("Nature de l'opération")
    cpte_deb = fields.Char("Compte Débit")
    cpte_cred = fields.Char("Compte Crébit")
    mnt_deb = fields.Float("Montant Débit")
    mnt_cred = fields.Float("Montant Crébit")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaJournalOperation(models.Model):
    _name = "compta_journal_operation"
    
    dte_deb = fields.Date("Du", required = True)
    dte_fin = fields.Date("Au", required = True)
    operation_lines = fields.One2many("compta_journal_operation_lines", "operation_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaJournalOperationLines(models.Model):
    _name = "compta_journal_operation_lines"
    
    operation_id = fields.Many2one("compta_journal_operation")
    dte = fields.Date("Date")
    refpiece = fields.Char("Ref Pièce")
    nature = fields.Char("Nature de l'opération")
    cpte_deb = fields.Char("Compte Débit")
    cpte_cred = fields.Char("Compte Crébit")
    mnt_deb = fields.Float("Montant Débit")
    mnt_cred = fields.Float("Montant Crébit")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

class ComptatEtatResteRecouvrer(models.Model):
    _name = "compta_etat_reste_recouvrer"
    
    name = fields.Char("NOM", default="Etat des restes à recouvrer")
    #lib = fields.Char(string="Name", "Etat des restes à recouvrer")
    dte_deb = fields.Date("Du", required = True)
    dte_fin = fields.Date("Au", required = True)
    reste_lines = fields.One2many("compta_etat_reste_recouvrer_lines", "reste_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        d_deb = self.dte_deb
        d_fin = self.dte_fin
        v_e = 'E%'

        for vals in self:
            vals.env.cr.execute("""select distinct t.cd_titre_recette as titre, t.contribuable_id as debiteur, t.dt_rec as dte, c.mnt_op_cpta as mnt_recouvre, t.mnt_rec as mnt_recouvrer, (t.mnt_rec - c.mnt_op_cpta) as reste 
            from budg_titrerecette t, compta_guichet_line c 
            where c.code1 like %s and t.company_id = %s and t.x_exercice_id = %s and t.dt_rec between %s and %s and t.et_doss = 'F' and c.ref_pj = t.cd_titre_recette """ ,(v_e,val_struct,val_ex, d_deb, d_fin))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.reste_lines.unlink()
            for line in rows:
                result.append((0,0, {'debiteur' : line['debiteur'],'titre' : line['titre'], 'dte': line['dte'], 'mnt_du': line['mnt_recouvrer'], 'mnt_rec': line['mnt_recouvre'], 'reste': line['reste'], }))
            self.reste_lines = result
            
        i = 0
        for x in self.reste_lines:
            i = i + 1
            x.ordre = i
    
class ComptaEtatResteRecouvrerLines(models.Model):
    _name = "compta_etat_reste_recouvrer_lines"
    
    ordre = fields.Integer()
    reste_id = fields.Many2one("compta_etat_reste_recouvrer", ondelete='cascade')
    debiteur = fields.Many2one("ref_contribuable","Débiteur")
    dte = fields.Date("Date d'emission")
    titre = fields.Char("N° Titre")
    mnt_du = fields.Float("Montant dû")
    mnt_rec = fields.Float("Montant recouvré")
    reste = fields.Float("Reste à recouvrer")
    observation = fields.Text("Observation")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptatEtatRestePayer(models.Model):
    _name = "compta_etat_reste_payer"
    
    name = fields.Char("Name", default="Etat des restes à payer")
    dte_deb = fields.Date("Du", required = True)
    dte_fin = fields.Date("Au", required = True)
    reste_lines = fields.One2many("compta_etat_reste_payer_lines", "reste_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        d_deb = self.dte_deb
        d_fin = self.dte_fin
        v_d = 'D%'

        for vals in self:
            vals.env.cr.execute("""select distinct e.no_beneficiaire as creancier, b.no_mandat as mdt, b.dt_etat as dte, c.montant as mnt_paye, b.mnt_ord as mnt_du, (b.mnt_ord - c.montant) as reste 
            from budg_engagement e, budg_mandat b, compta_cheq_dep c where e.no_eng = b.no_eng and c.code1 like %s and b.no_mandat = c.ref_pj
            and b.company_id = %s and b.x_exercice_id = %s and b.dt_etat between %s and %s and b.state = 'F' """ ,(v_d,val_struct,val_ex, d_deb, d_fin))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.reste_lines.unlink()
            for line in rows:
                result.append((0,0, {'creancier' : line['creancier'],'titre' : line['mdt'], 'dte': line['dte'], 'mnt_du': line['mnt_du'], 'mnt_rec': line['mnt_paye'], 'reste': line['reste'], }))
            self.reste_lines = result
        
        
        i = 0
        for x in self.reste_lines:
            i = i + 1
            x.ordre = i

class ComptaEtatRestePayerLines(models.Model):
    _name = "compta_etat_reste_payer_lines"
    
    ordre = fields.Integer()
    reste_id = fields.Many2one("compta_etat_reste_payer", ondelete='cascade')
    creancier = fields.Many2one("ref_beneficiaire","Créancier")
    dte = fields.Date("Date d'emission")
    titre = fields.Char("N° Mandat")
    mnt_du = fields.Float("Montant dû")
    mnt_rec = fields.Float("Montant payé")
    reste = fields.Float("Reste à payer")
    observation = fields.Text("Observation")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaROpLecr(models.Model):
    _name = "compta_r_op_lecr"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    id_op = fields.Integer()
    ty_op = fields.Char()
    no_lecr = fields.Integer()
    
class ComptaTeneurCompte(models.Model):
    _name = 'compta_teneur_compte'
    _rec_name = 'teneur'
    
    teneur = fields.Many2one("res.users", "Teneur de compte", required=True)
    teneur_line = fields.One2many("compta_teneur_compte_line", "teneur_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaTeneurCompteLine(models.Model):
    _name = 'compta_teneur_compte_line'
    _rec_name = "compte"
    
    teneur_id = fields.Many2one("compta_teneur_compte", ondelete="cascade")
    compte = fields.Many2one("compta_plan_line", "Compte", required=True)
    libelle = fields.Char("Libelle", readonly=True)
    sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crébit'),
        ('M', 'Mixte'),
        ], 'Sens', readonly= True)
    fg_attente = fields.Boolean("A", readonly= True)
    fg_financier = fields.Boolean("F", readonly= True)
    fg_lettrage = fields.Boolean("L", readonly= True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('compte')
    def val(self):
        if self.compte:
            self.libelle = self.compte.souscpte.lb_long
            self.sens = self.compte.fg_sens
            self.fg_attente = self.compte.fg_attente
            self.fg_financier = self.compte.fg_finance
            self.fg_lettrage = self.compte.fg_lettrage
    

class ComptaAntidaterEcriture(models.Model):
    _name = 'compta_antidater_ecriture'
    _rec_name ="no_ecr"
    
    no_ecr = fields.Integer("N° Ecriture", required=True)
    new_dte = fields.Date("Nouvelle date souhaitée", required=True)
    dte = fields.Date("Date actuelle", readonly=True)
    type = fields.Many2one("compta_type_ecriture","Type", readonly=True)
    origine = fields.Char("Origine", readonly=True)
    user_id = fields.Many2one("res.users", "Créateur", readonly=True)
    antidate_line = fields.One2many('compta_antidater_ecriture_line', 'antidate_id', readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
    def valider(self):
        
        v_ecr = int(self.no_ecr)
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_dt = self.new_dte
        
        self.env.cr.execute("UPDATE compta_ecriture set dt_ecriture = %s WHERE no_ecr = %s and company_id = %s and x_exercice_id = %s" ,(v_dt, v_ecr, v_struct, v_ex))
        self.env.cr.execute("UPDATE compta_ligne_ecriture set dt_ligne = %s WHERE no_ecr = %s and company_id = %s and x_exercice_id = %s" ,(v_dt, v_ecr, v_struct, v_ex))

    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_no_ecr = int(self.no_ecr)
        
        self.env.cr.execute("select dt_ecriture , type_ecriture , create_uid from compta_ecriture where no_ecr = %s and company_id = %s and x_exercice_id = %s" ,(v_no_ecr, val_struct,val_ex))
        res = self.env.cr.dictfetchall()
        self.dte = res and res[0]['dt_ecriture']
        self.user_id = res and res[0]['create_uid']
        self.type = res and res[0]['type_ecriture']
        
        for vals in self:
            vals.env.cr.execute("""select l.no_lecr as ligne, l.no_souscptes as cpte, l.lb_lecr as lib, l.type_pj as pj, l.fg_sens as sens, l.fg_etat as etat, l.mt_lecr  as mt
            from compta_ligne_ecriture l where l.no_ecr = %s and company_id = %s and x_exercice_id = %s""" ,(v_no_ecr, val_struct,val_ex))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.antidate_line.unlink()
            for line in rows:
                result.append((0,0, {'noligne' : line['ligne'],'compte' : line['cpte'], 'libelle': line['lib'], 'pj': line['pj'], 'sens': line['sens'], 'etat': line['etat'],'mnt': line['mt'] }))
            self.antidate_line = result
    

class ComptaAntidaterEcritureLine(models.Model):
    _name = "compta_antidater_ecriture_line"
    
    antidate_id = fields.Many2one('compta_antidater_ecriture')
    noligne = fields.Integer("N° Ligne")
    compte = fields.Many2one("ref_souscompte", 'Compte')
    pj = fields.Many2one("compta_piece","Type PJ")
    libelle = fields.Char("Libellé")
    sens = fields.Char("Sens")
    mnt = fields.Integer("Montant")
    etat = fields.Char("Etat")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaRejetLigne(models.Model):
    _name = 'compta_rejet_ligne'
    _rec_name = "no_ecr"
    
    no_ecr = fields.Integer("N° Ecriture", required = True)
    no_lecr = fields.Integer("N° Ligne Ecriture", required=True)
    dte = fields.Date("Date", readonly=True)
    sens = fields.Char("Sens", readonly=True)
    libelle = fields.Char("Libellé", readonly=True)
    compte = fields.Many2one("ref_souscompte", "Compte", readonly=True)
    mnt = fields.Integer("Montant", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
    def chercher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_no_ecr = int(self.no_ecr)
        v_lecr = int(self.no_lecr)
        self.env.cr.execute("""select l.dt_ligne, l.no_souscptes, l.lb_lecr, l.mt_lecr, l.fg_sens from compta_ligne_ecriture l, compta_ecriture e
        where l.no_ecr = e.no_ecr and e.no_ecr = %s and l.no_lecr = %s and l.x_exercice_id = %s and l.company_id = %s""" ,(v_no_ecr,v_lecr, val_ex, val_struct))
        res = self.env.cr.dictfetchall()
        self.dte = res and res[0]['dt_ligne']
        self.libelle = res and res[0]['lb_lecr']
        self.compte = res and res[0]['no_souscptes']
        self.mnt = res and res[0]['mt_lecr']
        self.sens = res and res[0]['fg_sens']
    
    def remise(self):
        
        v_ecr = int(self.no_ecr)
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_lecr = int(self.no_lecr)
        
        self.env.cr.execute("UPDATE compta_ligne_ecriture set fg_etat = 'P' WHERE no_ecr = %s and no_lecr = %s and company_id = %s and x_exercice_id = %s" ,(v_ecr, v_lecr, v_struct, v_ex))
      
class ComptaRegleOperationGuichet(models.Model):
    _name = "compta_regle_operation_guichet"
    _rec_name='typebase'
    
    typebase = fields.Many2one("compta_operation_guichet", "Type de base", required=True)
    code = fields.Char("Code", readonly=True)
    operation_guichet_ids = fields.One2many("compta_type_op_cpta", "regle_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
   
    
    @api.onchange('typebase')
    def Code(self):
        if self.typebase:
            self.code = self.typebase.code
            self.operation_guichet_ids = self.typebase.operation_guichet_ids
            

class ComptaRegleOperationBanque(models.Model):
    _name = "compta_regle_operation_banque"
    _rec_name='typebase'
    
    typebase = fields.Many2one("compta_operation_banque", "Type de base", required=True)
    code = fields.Char("Code", readonly=True)
    operation_banque_ids = fields.One2many("compta_type_op_banque", "regle_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
   
    
    @api.onchange('typebase')
    def Code(self):
        if self.typebase:
            self.code = self.typebase.code
            self.operation_banque_ids = self.typebase.operation_banque_ids


class ComptaPieces(models.Model):
    _name = "compta_pieces"
    _rec_name= "type2"
    
    type2 = fields.Many2one("compta_type_op_cpta","Opération de guichet", required=True)
    pieces_ids = fields.One2many("compta_piece_line", "pieces_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    def MaJ(self):
        v_id = int(self.id)
        v2 = int(self.type2)
        for x in self.pieces_ids:
            self.env.cr.execute("UPDATE compta_piece_line SET type2 = %d WHERE pieces_id = %d" %(v2,v_id))
        
    
class ComptaPieceLine(models.Model):
    _name = "compta_piece_line"
    _rec_name = "libelle"
    
    type2 = fields.Integer()
    pieces_id = fields.Many2one("compta_pieces", ondelete='cascade')
    libelle = fields.Many2one("ref_piece_justificatives", "Libellé de la pièce justificative")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    


class ComptaBrouillard(models.Model):
    _name ='compta_brouillard'
    
    name = fields.Char("nom", default="Brouillard")
    guichetier = fields.Many2one("compta_caisse_struct",domain="[('cd_us_caisse','=', user_id)]",required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True, default=lambda self: self.env.user)
    no_jour = fields.Integer("Journée guichet N°", readonly=True)
    dte = fields.Date("Journée du",default=fields.Date.context_today, readonly=False)
    encaisse = fields.Float("Encaisse au J-1", readonly=True)
    fondrecu = fields.Float("Fonds reçus ce jour", readonly=True)
    fondremi = fields.Float("Fonds remis ce jour", readonly=True)
    recette = fields.Float("Recettes du jour", readonly=True)
    depense = fields.Float("Dépenses du jour", readonly=True)
    total = fields.Float("Total du jour", readonly=True)
    solde = fields.Float("Solde du jour", readonly=True)
    recette_ids = fields.One2many("compta_br_recette", "br_id",string="Nature des recettes")
    depense_ids = fields.One2many("compta_br_depense", "br_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    @api.multi
    def afficher(self):
        val_ex = int(self.user_id.x_exercice_id)
        print("no_ex", val_ex)
        val_struct = int(self.company_id)
        print("struct", val_struct)
        v_id = int(self.guichetier)
        print("guichetier", v_id)
        v1_id = int(self.guichetier.cd_us_caisse)
        print("caissier", v1_id)
        
        self.env.cr.execute("select distinct g.no_jour from compta_jour_guichet g, compta_brouillard b where b.dte = g.dt_ouvert and g.company_id = %s and g.x_exercice_id = %s" ,(val_struct, val_ex))
        jr = self.env.cr.fetchone()
        jour = jr and jr[0]
        self.no_jour = jour
        
        v_jr = int(self.no_jour)
        print("jour",v_jr)
        
        self.env.cr.execute("""select sum( case when u.type_operation = 1 then l.mnt_op_cpta end) as recette
        from compta_guichet_line l, compta_guichet_unique u, compta_caisse_struct c
        where u.modreg = '0' and u.id = l.guichet_id and u.no_jour = %s and c.id = %s and l.company_id = %s and l.x_exercice_id = %s
        """ %(v_jr, v_id, val_struct, val_ex))
        r1 = self.env.cr.fetchone()
        self.recette = r1 and r1[0] or 0
        print("recette", self.recette)
        
        self.env.cr.execute("""select sum( case when u.type_operation = 2 then l.mnt_op_cpta end) as depense
        from compta_guichet_line l, compta_guichet_unique u, compta_caisse_struct c
        where u.modreg = '0' and u.id = l.guichet_id and u.no_jour = %s and c.id = %s and l.company_id = %s and l.x_exercice_id = %s
        """ %(v_jr, v_id, val_struct, val_ex))
        r2 = self.env.cr.fetchone()
        self.depense = r2 and r2[0] or 0
        print("depense",self.depense)
        
        self.total = self.recette + self.encaisse
        print("total",self.total)
        
        self.solde = self.total - self.depense
        print("solde",self.solde)
        
        
        for vals in self:
            vals.env.cr.execute("""select id as col from compta_colonne_caisse where cd_col_caise like 'D%' """)
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.depense_ids.unlink()
            for line in rows:
                result.append((0,0, {'colonne' : line['col']}))
            self.depense_ids = result
        
        
        for vals in self:
            vals.env.cr.execute("""select id as col from compta_colonne_caisse where cd_col_caise like 'R%' """)
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.recette_ids.unlink()
            for line in rows:
                result.append((0,0, {'colonne' : line['col']}))
            self.recette_ids = result
        
        self.Mnt()
        
    
    
    def Mnt(self):
        v_id = int(self.id)
        print("id actu", v_id)
        jr = int(self.no_jour)
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        user_id = int(self.guichetier.cd_us_caisse)
        print("fonction 2 guichet", user_id)
        v1_id = int(self.guichetier.cd_us_caisse)
        print("caissier2", v1_id)
      
        
        self.env.cr.execute("SELECT colonne from compta_br_depense where br_id = %d " %(v_id))
        
        for val in self.env.cr.dictfetchall():
            col = val['colonne']
            print("colonne", col)
            
            self.env.cr.execute("""select sum(l.mnt_op_cpta) as mnt from compta_guichet_line l, compta_operation_guichet o, compta_type_op_cpta t, compta_guichet_unique u
            where l.type1 = o.id and l.type2 = t.id and u.id = l.guichet_id and t.col_id = %d and l.company_id = %d and l.x_exercice_id = %d and u.type_operation = 2
            and u.no_jour = %d and u.gui_us = %d """ %(col,val_struct, val_ex, jr, user_id))
            res3 = self.env.cr.fetchone()
            mnt = res3 and res3[0] or 0
            mt = int(mnt)
            print("montatn dep", mt)
            self.env.cr.execute("UPDATE compta_br_depense SET mnt = %d where br_id = %d and colonne = %d " %(mt, v_id, col))
        
        
        self.env.cr.execute("SELECT colonne from compta_br_recette where br_id = %d " %(v_id))
        
        for val in self.env.cr.dictfetchall():
            colr = val['colonne']
            print("colonne rec", colr)
            
            self.env.cr.execute("""select sum(l.mnt_op_cpta) as mnt from compta_guichet_line l, compta_operation_guichet o, compta_type_op_cpta t, compta_guichet_unique u
            where l.type1 = o.id and l.type2 = t.id and u.id = l.guichet_id and t.col_id = %s and l.company_id = %d and l.x_exercice_id = %d and u.type_operation = 1
            and u.no_jour = %d and u.gui_us = %d """ %(colr, val_struct, val_ex, jr, user_id))
            res1 = self.env.cr.fetchone()
            mnt1 = res1 and res1[0] or 0
            mt1 = int(mnt1)
            print("montatn rec", mt)
            self.env.cr.execute("UPDATE compta_br_recette SET mnt = %d where br_id = %d and colonne = %d " %(mt1, v_id, colr))
       


class ComptaBrRecette(models.Model):
    _name = "compta_br_recette"
    
    br_id = fields.Many2one("compta_brouillard", ondelete="cascade")
    colonne = fields.Many2one("compta_colonne_caisse", "Code colonne", readonly=True)
    mnt = fields.Float("Montant", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaBrDepense(models.Model):
    _name = "compta_br_depense"
    
    br_id = fields.Many2one("compta_brouillard", ondelete="cascade")
    colonne = fields.Many2one("compta_colonne_caisse","Code colonne", readonly=True)
    mnt = fields.Float("Montant", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaBrouillardCaisse(models.Model):
    _name ='compta_brouillard_caisse'
    
    name = fields.Char("nom", default="Brouillard")
    caissier = fields.Many2one("compta_caisse_struct",default=lambda self: self.env['compta_caisse_struct'].search([('fg_resp','=', True)]),readonly=True, string="Caissier principal")
    no_jour = fields.Integer("Journée caisse N°", readonly=True)
    dte = fields.Date("Journée de caisse du",default=fields.Date.context_today, readonly=False)
    encaisse = fields.Float("Encaisse au JJ", readonly=True)
    recette = fields.Float("Recettes du jour (en numéraire)", readonly=True)
    depense = fields.Float("Dépenses du jour", readonly=True)
    total = fields.Float("Total du jour (en numéraire)", readonly=True)
    solde = fields.Float("Solde du jour (en numéraire)", readonly=True)
    recette_ids = fields.One2many("compta_br_caisse_recette", "br_id",string="Nature des recettes")
    depense_ids = fields.One2many("compta_br_caisse_depense", "br_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    def afficher(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select distinct g.no_jour from compta_jour_guichet g, compta_brouillard b where b.dte = g.dt_ouvert and g.company_id = %s and g.x_exercice_id = %s" ,(val_struct, val_ex))
        jr = self.env.cr.fetchone()
        jour = jr and jr[0]
        self.no_jour = jour
        
        v_jr = int(self.no_jour)
        
        self.env.cr.execute("""select coalesce(sum( case when u.type_operation = 1 then l.mnt_op_cpta end),0) as recette
        from compta_guichet_line l, compta_guichet_unique u
        where u.modreg = '0' and u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and l.x_exercice_id = %s
        """ ,(v_jr, val_struct, val_ex))
        r1 = self.env.cr.fetchone()
        self.recette = r1 and r1[0] or 0
        
        self.env.cr.execute("""select coalesce(sum( case when u.type_operation = 2 then l.mnt_op_cpta end),0) as depense
        from compta_guichet_line l, compta_guichet_unique u
        where u.modreg = '0' and u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and l.x_exercice_id = %s
        """ ,(v_jr, val_struct, val_ex))
        r2 = self.env.cr.fetchone()
        self.depense = r2 and r2[0] or 0
        
        self.env.cr.execute("""select mnt_fermeture from compta_jour_caisse where no_jour = %s 
        and x_exercice_id = %s and company_id = %s""" ,(v_jr, val_ex, val_struct))
        r3 = self.env.cr.fetchone()
        self.encaisse = r3 and r3[0] or 0
        
        
        self.total = self.recette + self.encaisse
        
        self.solde = self.total - self.depense
        
        for vals in self:
            vals.env.cr.execute("""select id as col from compta_colonne_caisse where cd_col_caise like 'D%' """)
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.depense_ids.unlink()
            for line in rows:
                result.append((0,0, {'colonne' : line['col']}))
            self.depense_ids = result
        
        
        for vals in self:
            vals.env.cr.execute("""select id as col from compta_colonne_caisse where cd_col_caise like 'R%' """)
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.recette_ids.unlink()
            for line in rows:
                result.append((0,0, {'colonne' : line['col']}))
            self.recette_ids = result
      
        self.Mnt()
    
    def Mnt(self):
        v_id = int(self.id)
        print("id actu", v_id)
        jr = int(self.no_jour)
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
      
        
        self.env.cr.execute("SELECT colonne from compta_br_caisse_depense where br_id = %d " %(v_id))
        
        for val in self.env.cr.dictfetchall():
            col = val['colonne']
            print("colonne", col)
            
            self.env.cr.execute("""select sum(l.mnt_op_cpta) as mnt from compta_guichet_line l, compta_operation_guichet o, compta_type_op_cpta t, compta_guichet_unique u
            where l.type1 = o.id and l.type2 = t.id and u.id = l.guichet_id and t.col_id = %d and l.company_id = %d and l.x_exercice_id = %d and u.type_operation = 2
            and u.no_jour = %d""" %(col,val_struct, val_ex, jr))
            res3 = self.env.cr.fetchone()
            mnt = res3 and res3[0] or 0
            mt = int(mnt)
            print("montatn dep", mt)
            self.env.cr.execute("UPDATE compta_br_caisse_depense SET mnt = %d where br_id = %d and colonne = %d " %(mt, v_id, col))
        
        
        self.env.cr.execute("SELECT colonne from compta_br_caisse_recette where br_id = %d " %(v_id))
        
        for val in self.env.cr.dictfetchall():
            colr = val['colonne']
            print("colonne rec", colr)
            
            self.env.cr.execute("""select sum(l.mnt_op_cpta) as mnt from compta_guichet_line l, compta_operation_guichet o, compta_type_op_cpta t, compta_guichet_unique u
            where l.type1 = o.id and l.type2 = t.id and u.id = l.guichet_id and t.col_id = %s and l.company_id = %d and l.x_exercice_id = %d and u.type_operation = 1
            and u.no_jour = %d """ %(colr, val_struct, val_ex, jr))
            res1 = self.env.cr.fetchone()
            mnt1 = res1 and res1[0] or 0
            mt1 = int(mnt1)
            print("montatn rec", mt)
            self.env.cr.execute("UPDATE compta_br_caisse_recette SET mnt = %d where br_id = %d and colonne = %d " %(mt1, v_id, colr))

        

class ComptaBrRecetteCaisse(models.Model):
    _name = "compta_br_caisse_recette"
    
    br_id = fields.Many2one("compta_brouillard_caisse", ondelete="cascade")
    colonne = fields.Many2one("compta_colonne_caisse", "Code colonne", readonly=True)
    mnt = fields.Float("Montant", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaBrDepenseCaisse(models.Model):
    _name = "compta_br_caisse_depense"
    
    br_id = fields.Many2one("compta_brouillard_caisse", ondelete="cascade")
    colonne = fields.Many2one("compta_colonne_caisse","Code colonne", readonly=True)
    mnt = fields.Float("Montant", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaEncours(models.Model):
    _name = "compta_encours"
    
    name = fields.Char("Nom", default="En cours numéraire")
    journee = fields.Many2one("compta_jour_caisse", "Jourée de caisse", required = True)
    dte = fields.Date("Du", readonly=True)
    ouverture = fields.Float("Ouverture", readonly=True)
    fermeture = fields.Float("Fermeture", readonly=True)
    encours_line = fields.One2many("compta_encours_line", "encours_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    @api.onchange('journee')
    def jour(self):
        if self.journee:
            self.dte = self.journee.dt_ouvert
            self.ouverture = self.journee.mnt_ouverture
            self.fermeture = self.journee.mnt_fermeture
    
    def afficher(self):
        
        val_ex = int(self.x_exercice_id)
        v_dte = self.dte
        val_struct = int(self.company_id)
        v_jr = int(self.journee.no_jour)
        
        for vals in self:
            vals.env.cr.execute("""select distinct u.gui_us as guichetier,
            (select  g.mnt_ouverture from compta_jour_guichet g  where g.no_jour = %s and g.company_id = %s and g.dt_ouvert = %s) as ouverture,
            (select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.type_operation = 1 and u.modreg <> '0' and
            u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and u.date_ope = %s and u.state not in ('draft','A') ) as cheque,
            (select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.type_operation = 1 and u.modreg = '0' and
            u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and u.date_ope = %s and u.state not in ('draft','A')) as encaissenum,
            (select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.type_operation = 1 and
            u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and u.date_ope = %s and u.state not in ('draft','A')) as encaisse,
            (select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.type_operation = 2 and
            u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and u.date_ope = %s and u.state not in ('draft','A')) as decaisse,
            ((select sum(l.mnt_op_cpta) from compta_guichet_unique u, compta_guichet_line l where u.type_operation = 1 and u.modreg = '0' and
            u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and u.date_ope = %s and u.state not in ('draft','A')) + (select  g.mnt_ouverture from compta_jour_guichet g 
            where g.no_jour = %s and g.company_id = %s and g.dt_ouvert = %s)) as total
            from compta_guichet_line l, compta_guichet_unique u, compta_caisse_struct c, compta_jour_guichet g
            where u.id = l.guichet_id and u.no_jour = %s and l.company_id = %s and u.date_ope = %s and l.fg_etat <> 'A' and u.state not in ('draft','A')""" ,(v_jr,val_struct,v_dte,v_jr,val_struct,v_dte,v_jr,val_struct,v_dte,v_jr,val_struct,v_dte,v_jr,val_struct,v_dte,v_jr,val_struct,v_dte,v_jr,val_struct,v_dte,v_jr,val_struct,v_dte))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.encours_line.unlink()
            for line in rows:
                result.append((0,0, {'guichetier' : line['guichetier'],'jour_cheque' : line['cheque'],'jour_numeraire' : line['encaissenum'],'num_ouvert' : line['ouverture'],
                                     'total_num' : line['total'],'total_encaisse' : line['encaisse'],'total_decaisse' : line['decaisse']}))
            self.encours_line = result
        
    
class ComptaEncoursLine(models.Model):
    _name = "compta_encours_line"
    
    encours_id = fields.Many2one("compta_encours", ondelete="cascade")
    guichetier = fields.Many2one("res.users","Guichetier", readonly=True)
    jour_cheque = fields.Float("Journée chèque", readonly=True)
    jour_numeraire = fields.Float("Journée numéraire", readonly=True)
    num_ouvert = fields.Float("Numéraire à l'ouverture", readonly=True)
    total_num = fields.Float("Total numéraire", readonly=True)
    total_encaisse = fields.Float("Total encaissé", readonly=True)
    total_decaisse = fields.Float("Total décaissé", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

class ComptaFinPeriode(models.Model):
    _name = "compta_fin_periode"
    
    name = fields.Char("Nom", default="Fin de Période")
    periode_ouv = fields.Many2one("compta_periode", "Période Ouverte",domain=[('state', '=', 'O')])
    periode_fer = fields.Many2one("compta_periode", "Période Arretée",domain=[('state', '=', 'A')])
    periode_arr = fields.Many2one("compta_periode", "Période Arretée",domain=[('state', '=', 'A')])
    dtea_deb = fields.Date("Date début", readonly=True)
    dtea_fin = fields.Date("Date fin", readonly=True)
    dter_deb = fields.Date("Date début", readonly=True)
    dter_fin = fields.Date("Date fin", readonly=True)
    dtec_deb = fields.Date("Date début", readonly=True)
    dtec_fin = fields.Date("Date fin", readonly=True)
    motif_arret = fields.Text("Motif d'arrêt")
    motif_reouvrir = fields.Text("Motif de réouverture")
    motif_cloturer = fields.Text("Motif de clôture")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    @api.onchange('periode_ouv')
    def PO(self):
        if self.periode_ouv:
            self.dtea_deb = self.periode_ouv.dt_debut
            self.dtea_fin = self.periode_ouv.dt_fin
    
    @api.onchange('periode_fer')
    def PF(self):
        if self.periode_fer:
            self.dter_deb = self.periode_fer.dt_debut
            self.dter_fin = self.periode_fer.dt_fin
    
    @api.onchange('periode_arr')
    def PC(self):
        if self.periode_arr:
            self.dtec_deb = self.periode_arr.dt_debut
            self.dtec_fin = self.periode_arr.dt_fin
        
    def IsCloturable(self):
        v_deb = self.dtea_deb
        v_fin = self.dtea_fin
        val_struct = int(self.company_id)
        val_ex = int(self.x_exercice_id)
        
        self.env.cr.execute("""select count(*) from compta_ligne_ecriture where fg_etat in ('P','R') and dt_ligne
        between %s and %s and company_id = %s and x_exercice_id = %s""",(v_deb, v_fin, val_struct, val_ex))
        res = self.env.cr.fetchone()
        c1 = res and res[0] or 0
        
        if c1 > 0:
            raise ValidationError(_("Il exist des lignes non encore vérifiées ou rejetées."))
        
        self.env.cr.execute("""select count(*) from compta_jour_caisse where dt_ouvert
        between %s and %s and dt_fermeture is null and company_id = %s and x_exercice_id = %s""",(v_deb, v_fin, val_struct, val_ex))
        res1 = self.env.cr.fetchone()
        c2 = res1 and res1[0] or 0
        
        if c2 > 0:
            raise ValidationError(_("Il existe des journées de caisse encore ouvertes."))
        
        self.env.cr.execute("""select count(*) from compta_ecriture_deseq_line l where l.dt_ligne between %s and %s and l.company_id = %s and l.x_exercice_id = %s
        and l.mnt_debit <> l.mnt_credit """,(v_deb, v_fin, val_struct, val_ex))
        res3 = self.env.cr.fetchone()
        c3 = res3 and res3[0] or 0
        
        if c3 > 0:
            raise ValidationError(_("Il existe des ecritures en anomalies."))
        
        self.env.cr.execute("""select count(*) from compta_releve r where r.dt_releve between %s and %s and r.company_id = %s and r.x_exercice_id = %s
        and l.etat = 'C' """,(v_deb, v_fin, val_struct, val_ex))
        res4 = self.env.cr.fetchone()
        c4 = res4 and res4[0] or 0
        
        if c4 > 0:
            raise ValidationError(_("Il existe des relevés sans ecritures produites."))

    def arreter(self):
        v_id = int(self.periode_ouv.id)
        val_struct = int(self.company_id)
        val_ex = int(self.x_exercice_id)
        
        self.IsCloturable()
        self.env.cr.execute("UPDATE compta_periode SET state = 'A' WHERE id = %d and company_id = %d and x_exercice_id = %d" %(v_id, val_struct, val_ex))
        
    def reouvrir(self):
        vc_id = int(self.periode_fer.id)
        val_struct = int(self.company_id)
        val_ex = int(self.x_exercice_id)
        
        self.env.cr.execute("UPDATE compta_periode SET state = 'O' WHERE id = %d and company_id = %d and x_exercice_id = %d" %(vc_id, val_struct, val_ex))

    def cloturer(self):
        vf_id = int(self.periode_fer.id)
        val_struct = int(self.company_id)
        val_ex = int(self.x_exercice_id)
        
        self.env.cr.execute("UPDATE compta_periode SET state = 'F' WHERE id = %d and company_id = %d and x_exercice_id = %d" %(vf_id, val_struct, val_ex))


class ComptaCorrectionOpGuichet(models.Model):
    _name = "compta_correction_op_guichet"
    
    name = fields.Char("Nom", default='Correction/Annulation Opération')
    type_operation = fields.Selection([
        ('C', 'Correction'),
        ('A', 'Annulation')
        ],string='Type Opération', required = True, default="C")
    operation = fields.Integer("N° Opération", required=False)
    operations = fields.Many2one("compta_guichet_unique","N° Opération", required=True)
    periode = fields.Many2one("compta_periode","Période",domain=[('state', '=', 'O')])
    dt_deb = fields.Date()
    dt_fin = fields.Date()
    no_jour = fields.Integer("N° Jour")
    dte_op = fields.Date("Date")
    categorie = fields.Selection([
        ('E', 'Encaissement'),
        ('D', 'Décaissement'),
        ('I', 'Indifférent')
        ], string="Catégorie opération")
    guichetier = fields.Selection([
        ('1', '1'),
        ('T', 'Tous')
        ], string = 'Précision guichetier')
    guichetier_id = fields.Many2one("compta_caisse_struct", "Guichetier")
    type_benef = fields.Many2one('compta_type_interv_ext', readonly=True)
    beneficiaire = fields.Char("Bénéficiaire", readonly=True)
    modereg = fields.Many2one("compta_jr_mode", "Mode règlement", readonly=True)
    mnt_total = fields.Float("Montant total", readonly=True)
    gui_us = fields.Many2one("compta_caisse_struct","Guichetier", readonly=True)
    fg_etat = fields.Char("Etat",readonly=True)
    no_ecr = fields.Char("Ecriture",readonly=True)
    correction_line = fields.One2many("compta_correction_op_guichet_line", "correction_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    gui_us = fields.Many2one('res.users',default=lambda self: self.env.user)


    # Récupérer l'exercice de l'utilisateur poour effectuer les traitements sur ça
    @api.onchange('gui_us')
    def User(self):
        if self.gui_us:
            self.x_exercice_id = self.gui_us.x_exercice_id
    
    @api.onchange('periode')
    def Periode(self):
        if self.periode:
            self.dt_deb = self.periode.dt_debut
            self.dt_fin = self.periode.dt_fin
            
    
    def chercher(self):

        v_ex1 = int(self.gui_us.x_exercice_id)
        self.x_exercice_id = v_ex1
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_op = int(self.operations)
        v_deb = self.dt_deb
        v_fin = self.dt_fin
        v_jr = int(self.no_jour)
        #v_gui = int(self.gui_us.cd_us_caisse)
        v_dte = self.dte_op
        v_cat = self.categorie
        
        self.env.cr.execute("""select distinct mode_reglement as mode, mnt_total as total, u.nom_usager as benef, u.state as state
        from compta_guichet_line l, compta_guichet_unique u 
        where u.id = l.guichet_id and u.x_exercice_id = %d and u.company_id = %d
        and u.id = %d""" %(v_ex, v_struct, v_op))
        res = self.env.cr.dictfetchall()
        #self.type_benef = res and res[0]['typebenef']
        self.beneficiaire = res and res[0]['benef']
        self.fg_etat = res and res[0]['state']
        self.mnt_total = res and res[0]['total']
        self.modereg = res and res[0]['mode']
        
        if self.operations and self.periode:
            for vals in self:
                vals.env.cr.execute("""select code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s and date_ope between %s and %s""" ,(v_ex, v_struct, v_op, v_deb, v_fin))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],
                                         'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result
                
        elif self.operations and self.no_jour:
            for vals in self:
                vals.env.cr.execute("""select distinct code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s and j.no_jour = %s""" ,(v_ex, v_struct, v_op, v_jr))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result
        
        elif self.operations and self.dte_op:
            for vals in self:
                vals.env.cr.execute("""select code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s and u.date_ope = %s""" ,(v_ex, v_struct,v_op, v_dte))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],
                                         'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result
        
        elif self.operations and self.categorie == 'E':
            for vals in self:
                vals.env.cr.execute("""select code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s and u.type_operation = '1' """ ,( v_ex, v_struct, v_op))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],
                                         'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result
        
        elif self.operations and self.categorie == 'D':
            for vals in self:
                vals.env.cr.execute("""select code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s and u.type_operation = '2' """ ,(v_ex, v_struct, v_op))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],
                                         'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result
            
        elif self.operations and self.categorie == 'I':
            for vals in self:
                vals.env.cr.execute("""select code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s and u.type_operation in ('1','2' )""" ,(v_ex, v_struct,v_op))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],
                                         'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result

        elif self.operations and self.guichetier == '1':
            for vals in self:
                vals.env.cr.execute("""select code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s and u.gui_us = %s""" ,(v_ex, v_struct,v_op, v_gui))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],
                                         'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result
        
        elif self.operations and self.guichetier == 'T':
            for vals in self:
                vals.env.cr.execute("""select code1 as c1, type1 as t1, code2 as c2, type2 as t2, mnt_op_cpta as mnt, pj as piece, ref_pj as ref, an_pj as annee, id_imput as imput
                from compta_guichet_line l, compta_guichet_unique u, compta_jour_guichet j 
                where u.id = l.guichet_id and u.x_exercice_id = %s and u.company_id = %s
                and u.id = %s""" ,(v_ex, v_structv_op,))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.correction_line.unlink()
                for line in rows:
                    result.append((0,0, {'code1' : line['c1'],'type1' : line['t1'],'code2' : line['c2'],'type2' : line['t2'],
                                         'mnt_actuel' : line['mnt'],'piece' : line['piece'],'ref' : line['ref'],'annee' : line['annee'],'imput' : line['imput']}))
                self.correction_line = result
        
    
    def corriger(self):
        
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_op = int(self.operations)
        
        for vals in self.correction_line:
            v_mnt = vals.new_mnt
            v_c1 = vals.code1
            v_t1 = vals.type1.id
            v_c2 = vals.code2
            v_t2 = vals.type2.id
            v_pj = vals.piece.id
            v_ref = vals.ref
            v_imput = vals.imput.id
            if vals.ok == True:
                self.env.cr.execute("""UPDATE compta_guichet_line SET mnt_op_cpta = %s WHERE guichet_id = (select id from 
                compta_guichet_unique where id = %s and x_exercice_id = %s and company_id = %s) and code1 = %s and
                type1 = %s and code2 = %s and type2 = %s and pj = %s and ref_pj = %s and id_imput = %s
                 """ ,(v_mnt,v_op, v_ex, v_struct, v_c1, v_t1, v_c2, v_t2, v_pj, v_ref, v_imput))
                
        self.env.cr.execute("""SELECT sum(l.mnt_op_cpta) from compta_guichet_line l, compta_guichet_unique u where l.guichet_id = u.id and u.no_op = %d and u.company_id = %d and 
        l.x_exercice_id = %d """ %(v_op, v_struct, v_ex))
        res = self.env.cr.fetchone()
        mnt = res and res[0] or 0
                
        self.env.cr.execute("""UPDATE compta_guichet_unique SET mnt_total = %s WHERE id = %s and x_exercice_id = %s and company_id = %s """,(mnt, v_op, v_ex, v_struct))

    def annuler(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_op = int(self.operations)
        
        self.env.cr.execute("""UPDATE compta_guichet_unique SET state = 'A' WHERE id = %s and x_exercice_id = %s and company_id = %s """,(v_op, v_ex, v_struct))

        self.env.cr.execute("""UPDATE compta_guichet_line SET fg_etat = 'A' WHERE guichet_id = %s and x_exercice_id = %s and company_id = %s """,(v_op, v_ex, v_struct))

        

class ComptaCorrectionOpGuichetLine(models.Model):
    _name = "compta_correction_op_guichet_line"
    
    correction_id = fields.Many2one("compta_correction_op_guichet",ondelete='cascade')
    code1 = fields.Char("Code", readonly=True)
    type1 = fields.Many2one("compta_operation_guichet", "Catégorie opération", readonly=True)
    code2 = fields.Char("Code 2", readonly=True)
    type2 = fields.Many2one("compta_type_op_cpta","Nature opération", readonly=True)
    mnt_actuel = fields.Float("Montant actuel", readonly=True)
    new_mnt = fields.Float("Nouveau montant")
    piece = fields.Many2one("compta_piece_line", "Pièce", readonly=True)
    ref = fields.Char("Ref Pièce", readonly=True)
    annee = fields.Many2one("ref_exercice", "Année pièce", readonly=True)
    imput = fields.Many2one("ref_souscompte", "Imputation", readonly=True)
    ok = fields.Boolean("Ok ?")
    

class ComptaValidationEcriture(models.Model):
    _name = "compta_validation_ecriture"
    
    name = fields.Char("Nom",default="Validation Ecriture")
    type_op = fields.Selection([
        ('I', 'Indifférents'),
        ('V', 'Validables'),
        ('NV', 'Non validables'),
        ('A', 'Anomalie'),
        ], string = "Type Op", required = False)
    dte = fields.Date("Date de création supérieur à")
    dt_valid = fields.Date(default=fields.Date.context_today)
    type = fields.Many2one("compta_type_ecriture", "Type écriture")
    origine = fields.Many2one("compta_type_op_ecriture", "Origine")
    no_ecr = fields.Integer("N° Ecriture")
    validation_line = fields.One2many("compta_validation_ecriture_line", "validation_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    def chercher(self):
        val_ex = int(self.company_id)
        val_struct = int(self.x_exercice_id)
        v_or = self.origine.type_op_ecr
        v_typ = int(self.type.id)
        v_dte = self.dte
        v_ecr = int(self.no_ecr)
        if self.type:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_ecr as ecr, l.no_lecr as lecr, l.no_souscptes as cpte, l.lb_lecr as lib, l.fg_sens as sens, l.mt_lecr as mt, l.fg_etat as etat from compta_ligne_ecriture l,
                compta_ecriture u where u.type_ecriture = %s and u.no_ecr = l.no_ecr and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat = 'V' order by l.no_ecr""" ,(v_typ,val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.validation_line.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['ecr'], 'nolecr': line['lecr'], 'compte': line['cpte'], 'libelle': line['lib'], 'sens': line['sens'], 
                    'montant': line['mt'],'etat': line['etat']}))
                self.validation_line = result
        elif self.origine:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_ecr as ecr, l.no_lecr as lecr, l.no_souscptes as cpte, l.lb_lecr as lib, l.fg_sens as sens, l.mt_lecr as mt, l.fg_etat as etat from compta_ligne_ecriture l,
                compta_ecriture u where u.type_op = %s and u.no_ecr = l.no_ecr and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat = 'V' order by l.no_ecr""" ,(v_or,val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.validation_line.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['ecr'], 'nolecr': line['lecr'], 'compte': line['cpte'], 'libelle': line['lib'], 'sens': line['sens'], 
                    'montant': line['mt'],'etat': line['etat']}))
                self.validation_line = result
        elif self.dte:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_ecr as ecr, l.no_lecr as lecr, l.no_souscptes as cpte, l.lb_lecr as lib, l.fg_sens as sens, l.mt_lecr as mt, l.fg_etat as etat from compta_ligne_ecriture l,
                compta_ecriture u where u.dt_ecriture > %s and u.no_ecr = l.no_ecr and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat = 'V' order by l.no_ecr""" ,(v_dte,val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.validation_line.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['ecr'], 'nolecr': line['lecr'], 'compte': line['cpte'], 'libelle': line['lib'], 'sens': line['sens'], 
                    'montant': line['mt'],'etat': line['etat']}))
                self.validation_line = result
        elif self.no_ecr:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_ecr as ecr, l.no_lecr as lecr, l.no_souscptes as cpte, l.lb_lecr as lib, l.fg_sens as sens, l.mt_lecr as mt, l.fg_etat as etat from compta_ligne_ecriture l,
                compta_ecriture u where u.no_ecr = %s and u.no_ecr = l.no_ecr and l.x_exercice_id = %s and l.company_id = %s and l.fg_etat = 'V' order by l.no_ecr""" ,(v_ecr,val_ex, val_struct))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.validation_line.unlink()
                for line in rows:
                    result.append((0,0, {'no_ecr' : line['ecr'], 'nolecr': line['lecr'], 'compte': line['cpte'], 'libelle': line['lib'], 'sens': line['sens'], 
                    'montant': line['mt'],'etat': line['etat']}))
                self.validation_line = result
    
    def valider(self):
        val_ex = int(self.company_id)
        val_struct = int(self.x_exercice_id)
        v_dte = self.dt_valid
        v_id = int(self.id)
        
        
        self.env.cr.execute("""select no_ecr, nolecr from compta_validation_ecriture_line where validation_id = %s and x_exercice_id = %s and company_id = %s """ ,(v_id, val_ex, val_struct))
        
        for x in self.env.cr.dictfetchall():
            ecr = x['no_ecr']
            lecr = x['nolecr']
            
            self.env.cr.execute("""UPDATE compta_ecriture SET state = 'W', dt_valid = %s WHERE x_exercice_id = %s and company_id = %s and no_ecr = %s """ ,(v_dte, val_ex, val_struct, ecr))
            
            self.env.cr.execute("""UPDATE compta_ligne_ecriture SET fg_etat = 'W', dt_valid = %s WHERE x_exercice_id = %s and company_id = %s and
            no_ecr = %s and no_lecr = %s""",(v_dte, val_ex, val_struct, ecr, lecr))

class ComptaValidationEcritureLine(models.Model):
    _name = "compta_validation_ecriture_line"

    validation_id = fields.Many2one("compta_validation_ecriture", ondelete='cascade')
    no_ecr = fields.Integer("N° Ecriture")
    nolecr = fields.Integer("N° Ligne", readonly=True)
    compte = fields.Many2one("ref_souscompte", "Compte", readonly=True)
    libelle = fields.Char("Libellé", readonly=True)
    sens = fields.Char("Sens", readonly=True)
    montant = fields.Char("Montant", readonly=True)
    etat = fields.Char("Etat", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

class ComptaEcritureRegularisation(models.Model):
    _name = "compta_ecriture_regularisation"
    
    name = fields.Char("Nom", default="Ecriture de régularisation")
    compte = fields.Many2one("compta_teneur_compte_line", "Compte", domain = ['|',("fg_attente","=",True),("fg_financier","=",True)], required=True)
    imput = fields.Integer()
    libelle = fields.Char("Libellé", readonly =True)
    noecr = fields.Integer("Ecriture")
    no_lecr = fields.Integer("Ligne")
    solde = fields.Integer("Solde à régulariser", readonly =True)
    noecr = fields.Integer("Ecriture")
    dte = fields.Date(default=fields.Date.context_today)
    f_sens = fields.Char("Sens", readonly =True)
    mnt_regul = fields.Integer("Montant régularisé",readonly =True)
    rest_regul = fields.Integer("Reste à régulariser",readonly =True)
    type_ecriture = fields.Many2one("compta_type_ecriture", 'Type ecriture', default=lambda self: self.env['compta_type_ecriture'].search([('type_ecriture','=', 'U')])) 
    regularisation_line = fields.One2many("compta_ecriture_regularisation_line", "regularisation_id")
    regularisation_ids = fields.One2many("compta_ecriture_regularisation_ids", "regularisation_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    
    @api.onchange('compte')
    def get_imput(self):
        if self.compte:
            self.imput = self.compte.compte.souscpte.id
            self.libelle = self.compte.compte.souscpte.lb_long
    
    
    def chercher(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        imput = int(self.imput)
        ecr = int(self.noecr)
        lecr = int(self.no_lecr)
        
        
        if self.compte:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.x_exercice_id as annee, l.ref_pj as ref, l.fg_sens as sens, l.mt_lecr as mt from compta_ligne_ecriture l
                where l.x_exercice_id = %s and l.company_id = %s and l.no_souscptes = %s and  l.fg_etat in ('V','W') order by l.no_lecr""" ,(val_ex, val_struct, imput))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.regularisation_line.unlink()
                for line in rows:
                    result.append((0,0, {'ligne' : line['ligne'], 'annee': line['annee'], 'ref': line['ref'], 'sens': line['sens'], 
                    'montant': line['mt']}))
                self.regularisation_line = result
        elif self.compte and self.noecr:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.x_exercice_id as annee, l.ref_pj as ref, l.fg_sens as sens, l.mt_lecr as mt from compta_ligne_ecriture l
                where l.x_exercice_id = %s and l.company_id = %s and l.no_souscptes = %s and l.no_ecr = %s and  l.fg_etat in ('V','W') order by l.no_lecr""" ,(val_ex, val_struct, imput, ecr))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.regularisation_line.unlink()
                for line in rows:
                    result.append((0,0, {'ligne' : line['ligne'], 'annee': line['annee'], 'ref': line['ref'], 'sens': line['sens'], 
                    'montant': line['mt']}))
                self.regularisation_line = result
        elif self.compte and self.no_lecr:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.x_exercice_id as annee, l.ref_pj as ref, l.fg_sens as sens, l.mt_lecr as mt from compta_ligne_ecriture l
                where l.x_exercice_id = %s and l.company_id = %s and l.no_souscptes = %s and l.no_lecr = %s and l.fg_etat in ('V','W') order by l.no_lecr""" ,(val_ex, val_struct, imput, lecr))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.regularisation_line.unlink()
                for line in rows:
                    result.append((0,0, {'ligne' : line['ligne'], 'annee': line['annee'], 'ref': line['ref'], 'sens': line['sens'], 
                    'montant': line['mt']}))
                self.regularisation_line = result
                
    def voir(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.id)
        
        self.env.cr.execute("""select sum(montant) from compta_ecriture_regularisation_line where regularisation_id = %d
        and company_id = %d and x_exercice_id = %d and sens = 'C' and regul = True group by sens """ %(v_id, val_struct, val_ex))
        res_c = self.env.cr.fetchone()
        val_c = res_c and res_c[0] or 0
        
        self.env.cr.execute("""select sum(montant) from compta_ecriture_regularisation_line where regularisation_id = %d
        and company_id = %d and x_exercice_id = %d and sens = 'D' and regul = True group by sens """ %(v_id, val_struct, val_ex))
        res_d = self.env.cr.fetchone()
        val_d = res_d and res_d[0] or 0
        
        self.solde = abs(val_d - val_c)
        

    
    def calculer(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.id)
        
        self.env.cr.execute("""select sum(montant) from compta_ecriture_regularisation_ids where regularisation_id = %d
        and company_id = %d and x_exercice_id = %d""" %(v_id, val_struct, val_ex))
        res = self.env.cr.fetchone()
        self.mnt_regul = res and res[0] or 0

        
        self.env.cr.execute("""select sens from compta_ecriture_regularisation_ids where regularisation_id = %d
        and company_id = %d and x_exercice_id = %d""" %(v_id, val_struct, val_ex))
        for x in self.env.cr.dictfetchall():
            v_sens = x['sens']
        
        if v_sens == 'D':
            self.rest_regul = self.solde - self.mnt_regul
        else:
            self.rest_regul = self.solde + self.mnt_regul
            
        
        
                
        
    def regulariser(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.id)
        typ_ecr = int(self.type_ecriture)
        v_dte = self.dte
        var_cptes = int(self.imput)
        
        self.env.cr.execute("""SELECT coalesce(sum(montant),0) from compta_ecriture_regularisation_ids WHERE regularisation_id = %d
        and company_id = %d and x_exercice_id = %d and sens = 'D' """ %(v_id, val_struct, val_ex))
        res = self.env.cr.fetchone()
        mnt_d = res and res[0] or 0
        
        self.env.cr.execute("""SELECT coalesce(sum(montant),0) from compta_ecriture_regularisation_ids WHERE regularisation_id = %d
        and company_id = %d and x_exercice_id = %d and sens = 'C' """ %(v_id, val_struct, val_ex))
        res1 = self.env.cr.fetchone()
        mnt_c = res1 and res1[0] or 0
        
        if mnt_c >= mnt_d:
            mnt_p = mnt_c - mnt_d
            self.f_sens = 'C'
        else:
            mnt_p = mnt_d - mnt_c
            self._sens = 'D'
            
        self.env.cr.execute("select no_ecr,no_lecr from compta_compteur_ecr where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
        noecr = self.env.cr.dictfetchall()
        no_ecrs = noecr and noecr[0]['no_ecr']
        no_ecrs1 = noecr and noecr[0]['no_lecr']
        no_ecr = no_ecrs
        
        v_no_ecr = no_ecr + 1
        self.env.cr.execute("INSERT INTO compta_ecriture(no_ecr, dt_ecriture, type_ecriture, type_journal, type_op ,x_exercice_id, company_id, state) VALUES (%s, %s, %s, %s, 'L', %s, %s, 'P')" ,(v_no_ecr, v_dte, typ_ecr, None, val_ex, val_struct))

        v_lecr = no_ecrs1 + 1
        var_ecr = v_no_ecr
        
        if mnt_c != 0:
            #v_lblecr = 'L-U'+ ' ' + str(self.regularisation_ids.exercice.no_ex) + ' ' + str(self.regularisation_ids.ref)
            
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, 'D', %s, 'F') """ ,(var_ecr,v_lecr, var_cptes, mnt_c, val_ex, val_struct, v_dte))
        
        v_nolecr = v_lecr + 1
        if mnt_d != 0:
            #v_lblecr = 'L-U'+ ' ' + str(self.regularisation_ids.exercice.no_ex) + ' ' + str(self.regularisation_ids.ref)
            
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr,no_lecr, no_souscptes, mt_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, 'C', %s, 'F') """ ,(var_ecr,v_nolecr, var_cptes, mnt_d, val_ex, val_struct, v_dte))
    
        self.env.cr.execute("""SELECT sens, imputation, montant, piece, ref, exercice from compta_ecriture_regularisation_ids
        WHERE regularisation_id = %d and company_id = %d and x_exercice_id = %d""" %(v_id, val_struct, val_ex))
        
        for val in self.env.cr.dictfetchall():
            v_nolecr = v_nolecr + 1
            sens = val['sens']
            var_cptes = val['imputation']
            v_mnt = val['montant']
            v_piece = val['piece']
            v_ref = val['ref']
            v_ex = val['exercice']
            v_lblecr = 'L-U'+ '-' + str(v_ex) + '-' + str(v_ref)
            
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture(no_ecr, no_lecr, no_souscptes, mt_lecr, lb_lecr, x_exercice_id, company_id, fg_sens, dt_ligne, fg_etat) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'P') """ ,(var_ecr,v_nolecr, var_cptes, v_mnt, v_lblecr, val_ex, val_struct, sens, v_dte))
    
        
        self.env.cr.execute("UPDATE compta_compteur_ecr SET no_ecr = %s, no_lecr = %s WHERE company_id = %s and x_exercice_id = %s" ,(var_ecr, v_nolecr, val_struct, val_ex))
        
        
class ComptaEcritureRegularisationLine(models.Model):
    _name = "compta_ecriture_regularisation_line"
    
    regularisation_id = fields.Many2one("compta_ecriture_regularisation", ondelete='cascade')
    ligne = fields.Integer("Ligne", readonly=True)
    annee = fields.Many2one("ref_exercice","Année PJ", readonly=True)
    ref = fields.Char("Ref PJ", readonly=True)
    sens = fields.Char("Sens", readonly=True)
    montant = fields.Integer("Montant", readonly=True)
    regul = fields.Boolean("Régulariser ?")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    

class ComptaEcritureRegularisationIds(models.Model):
    _name = "compta_ecriture_regularisation_ids"
    
    regularisation_id = fields.Many2one("compta_ecriture_regularisation", ondelete='cascade')
    compte = fields.Many2one("compta_plan_line", "Compte regul.", required=True )
    sens = fields.Selection([
        ('D', 'Débit'),
        ('C', 'Crédit'),
        ], string="Sens", required=True)
    imputation = fields.Integer()
    montant = fields.Integer("Montant", required=True)
    piece = fields.Many2one("ref_piece_justificatives","PJ", required =True)
    ref = fields.Char("Ref", required =True)
    exercice = fields.Many2one("ref_exercice", string="Exercice", required =True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    


    @api.onchange('compte')
    def Imputation(self):
        
        if self.compte:
            self.imputation = self.compte.souscpte.id


class ComptaLettrage(models.Model):
    _name = "compta_lettrage"
    
    name = fields.Char("Nom", default="Lettrage")
    compte = fields.Many2one("compta_plan_line", "Compte",domain = [("fg_lettrage","=",True)], required=True )
    dte_avant = fields.Date("Date avant")
    dte_apres = fields.Date("Date apres")
    mnt_credit = fields.Integer("Crédit", readonly=True)
    mnt_debit = fields.Integer("Débit", readonly=True)
    nbre_debit = fields.Integer("Nbr Ligne Débit", readonly=True)
    nbre_credit = fields.Integer("Nbr Ligne Crédit", readonly=True)
    solde = fields.Integer("Solde", readonly=True)
    solde_sens = fields.Char("", readonly=True)
    debit_total = fields.Integer("Total Débit", readonly=True)
    credit_total = fields.Integer("Total Crédit", readonly=True)
    total_d = fields.Integer("Total coché débit", readonly=True)
    total_c = fields.Integer("Total coché crédit", readonly=True)
    lettrage_debit_ids = fields.One2many("compta_lettrage_debit", "lettrage_id")
    lettrage_credit_ids = fields.One2many("compta_lettrage_credit", "lettrage_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    def chercher(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        imput = int(self.compte.souscpte.id)
        dt_av = self.dte_avant
        dt_ap = self.dte_apres
        
        if self.compte:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.dt_ligne as dt, r.no_ex ||'/'|| l.ref_pj as ref, l.mt_lecr as mt from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W') order by l.no_lecr""" ,(val_ex, val_struct, imput))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.lettrage_debit_ids.unlink()
                for line in rows:
                    result.append((0,0, {'dte' : line['dt'], 'ligne': line['ligne'], 'pj': line['ref'], 'mnt': line['mt']}))
                self.lettrage_debit_ids = result
                
                self.env.cr.execute("""select count(l.id) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W')""" ,(val_ex, val_struct, imput))
                val = self.env.cr.fetchone()
                self.nbre_debit = val and val[0] or 0
                
                self.env.cr.execute("""select sum(l.mt_lecr) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W')""" ,(val_ex, val_struct, imput))
                vals= self.env.cr.fetchone()
                self.debit_total = vals and vals[0] or 0
            
            
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.dt_ligne as dt, r.no_ex ||'/'|| l.ref_pj as ref, l.mt_lecr as mt from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W') order by l.no_lecr""" ,(val_ex, val_struct, imput))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.lettrage_credit_ids.unlink()
                for line in rows:
                    result.append((0,0, {'dte' : line['dt'], 'ligne': line['ligne'], 'pj': line['ref'], 'mnt': line['mt']}))
                self.lettrage_credit_ids = result
                
                self.env.cr.execute("""select count(l.id) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W')""" ,(val_ex, val_struct, imput))
                val = self.env.cr.fetchone()
                self.nbre_credit= val and val[0] or 0
                
                self.env.cr.execute("""select sum(l.mt_lecr) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W')""" ,(val_ex, val_struct, imput))
                vals = self.env.cr.fetchone()
                self.credit_total= vals and vals[0] or 0
        
        if self.compte and self.dte_avant:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.dt_ligne as dt, r.no_ex ||'/'|| l.ref_pj as ref, l.mt_lecr as mt from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W') and dt_ligne < %s order by l.no_lecr""" ,(val_ex, val_struct, imput, dt_av))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.lettrage_debit_ids.unlink()
                for line in rows:
                    result.append((0,0, {'dte' : line['dt'], 'ligne': line['ligne'], 'pj': line['ref'], 'mnt': line['mt']}))
                self.lettrage_debit_ids = result
                
                self.env.cr.execute("""select sum(l.mt_lecr) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W') and dt_ligne < %s """ ,(val_ex, val_struct, imput, dt_av))
                vals = self.env.cr.fetchone()
                self.debit_total = vals and vals[0] or 0
                
                self.env.cr.execute("""select count(l.id) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W') and dt_ligne < %s """ ,(val_ex, val_struct, imput, dt_av))
                val = self.env.cr.fetchone()
                self.nbre_debit = val and val[0] or 0
            
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.dt_ligne as dt, r.no_ex ||'/'|| l.ref_pj as ref, l.mt_lecr as mt from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W') and dt_ligne < %s order by l.no_lecr""" ,(val_ex, val_struct, imput, dt_av))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.lettrage_credit_ids.unlink()
                for line in rows:
                    result.append((0,0, {'dte' : line['dt'], 'ligne': line['ligne'], 'pj': line['ref'], 'mnt': line['mt']}))
                self.lettrage_credit_ids = result
                
                self.env.cr.execute("""select count(l.id) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W') and dt_ligne < %s """ ,(val_ex, val_struct, imput, dt_av))
                val = self.env.cr.fetchone()
                self.nbre_credit = val and val[0] or 0
                
                self.env.cr.execute("""select sum(l.mt_lecr) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W') and dt_ligne < %s """ ,(val_ex, val_struct, imput, dt_av))
                vals = self.env.cr.fetchone()
                self.credit_total = vals and vals[0] or 0
        
        if self.compte and self.dte_apres:
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.dt_ligne as dt, r.no_ex ||'/'|| l.ref_pj as ref, l.mt_lecr as mt from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W') and dt_ligne > %s order by l.no_lecr""" ,(val_ex, val_struct, imput, dt_ap))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.lettrage_debit_ids.unlink()
                for line in rows:
                    result.append((0,0, {'dte' : line['dt'], 'ligne': line['ligne'], 'pj': line['ref'], 'mnt': line['mt']}))
                self.lettrage_debit_ids = result
                
                self.env.cr.execute("""select sum(l.mt_lecr) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W') and dt_ligne > %s """ ,(val_ex, val_struct, imput, dt_ap))
                vals = self.env.cr.fetchone()
                self.debit_total = vals and vals[0] or 0
                
                self.env.cr.execute("""select count(l.id) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'D' 
                and l.fg_etat in ('V','W') and dt_ligne > %s """ ,(val_ex, val_struct, imput, dt_av))
                val = self.env.cr.fetchone()
                self.nbre_debit = val and val[0] or 0
            
            
            for vals in self:
                vals.env.cr.execute("""select distinct l.no_lecr as ligne, l.dt_ligne as dt, r.no_ex ||'/'|| l.ref_pj as ref, l.mt_lecr as mt from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W') and dt_ligne > %s order by l.no_lecr""" ,(val_ex, val_struct, imput, dt_ap))
                rows = vals.env.cr.dictfetchall()
                result = []
                
                vals.lettrage_credit_ids.unlink()
                for line in rows:
                    result.append((0,0, {'dte' : line['dt'], 'ligne': line['ligne'], 'pj': line['ref'], 'mnt': line['mt']}))
                self.lettrage_credit_ids = result
        
                self.env.cr.execute("""select distinct count(l.id) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W') and dt_ligne > %s """ ,(val_ex, val_struct, imput, dt_ap))
                val = self.env.cr.fetchone()
                self.nbre_credit = val and val[0] or 0
                
                self.env.cr.execute("""select distinct sum(l.mt_lecr) from compta_ligne_ecriture l,
                ref_exercice r where l.x_exercice_id = %s and r.id = l.x_exercice_id and l.company_id = %s and l.no_souscptes = %s and fg_sens = 'C' 
                and l.fg_etat in ('V','W') and dt_ligne > %s """ ,(val_ex, val_struct, imput, dt_ap))
                val = self.env.cr.fetchone()
                self.credit_total = val and val[0] or 0
        
        self.mnt_credit = self.credit_total
        self.mnt_debit = self.debit_total
        
        self.solde = self.mnt_debit - self.mnt_credit
        if self.mnt_credit > self.mnt_debit:
            self.solde_sens = 'Créditeur'
        else:
            self.solde_sens = 'Débiteur'
    
    def calculer(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.id)
        
        self.env.cr.execute("""select sum(d.mnt) from compta_lettrage_debit d,compta_lettrage l
        where l.x_exercice_id = %d and l.company_id = %d and l.id = d.lettrage_id 
        and d.lettrage_id = %d and d.cocher = True""" %(val_ex, val_struct, v_id))
        val = self.env.cr.fetchone()
        self.total_d = val and val[0] or 0
        
        
        self.env.cr.execute("""select sum(c.mnt) from compta_lettrage_credit c,compta_lettrage l
        where l.x_exercice_id = %d and l.company_id = %d and l.id = c.lettrage_id 
        and c.lettrage_id = %d and c.cocher = True""" %(val_ex, val_struct, v_id))
        vals = self.env.cr.fetchone()
        self.total_c = vals and vals[0] or 0
    
    def lettrer(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.id)
        
        if self.total_c != self.total_d:
            raise ValidationError(_("Lettrage impossible. La somme des débits est différente de la somme des crédits."))
        
        self.env.cr.execute("""select d.cocher as cocher, d.ligne, as ligne from compta_lettrage_debit d,compta_lettrage l
        where l.x_exercice_id = %d and l.company_id = %d and l.id = d.lettrage_id 
        and d.lettrage_id = %d and d.cocher = True""" %(val_ex, val_struct, v_id))
        
        for val in self.env.cr.fetchall():
            etat1 = val['cocher']
            ligne1 = val['ligne']
            
            if etat1 == True:
                self.env.cr.execute("UPDATE compta_ligne_ecriture SET fg_etat = 'F' WHERE no_lecr = %s and company_id = %s and x_exercice_id = %s" ,(ligne1,val_struct, val_ex))

        
        self.env.cr.execute("""select c.cocher as cocher, c.ligne as ligne from compta_lettrage_credit c,compta_lettrage l
        where l.x_exercice_id = %d and l.company_id = %d and l.id = c.lettrage_id 
        and c.lettrage_id = %d and c.cocher = True""" %(val_ex, val_struct, v_id))
        
        for record in self.env.cr.fetchall():
            etat2 = record['cocher']
            ligne2 = record['ligne']
            
            if etat2 == True:
                self.env.cr.execute("UPDATE compta_ligne_ecriture SET fg_etat = 'I' WHERE no_lecr = %s and company_id = %s and x_exercice_id = %s" ,(ligne2,val_struct, val_ex))
        

class ComptaLettrageDebit(models.Model):
    _name = "compta_lettrage_debit"
    
    lettrage_id = fields.Many2one("compta_lettrage", ondelete ='cascade')
    dte = fields.Date("Date", readonly=True)
    ligne = fields.Integer("N° Ligne", readonly=True)
    pj = fields.Char("PJ(typ-an-re)", readonly=True)
    mnt = fields.Integer("Montant", readonly=True)
    cocher = fields.Boolean("Cocher ?")
    

class ComptaLettrageCredit(models.Model):
    _name = "compta_lettrage_credit"
    
    lettrage_id = fields.Many2one("compta_lettrage", ondelete ='cascade')
    dte = fields.Date("Date", readonly=True)
    ligne = fields.Integer("N° Ligne", readonly=True)
    pj = fields.Char("PJ(typ-an-re)", readonly=True)
    mnt = fields.Integer("Montant", readonly=True)
    cocher = fields.Boolean("Cocher ?")
    

class ComptaEnvoiLigneGS(models.Model):
    _name = "compta_envoi_ligne_gs"
    
    name = fields.Char("Nom", default="Envoi ligne gestion suivante")
    compte = fields.Many2one("compta_teneur_compte_line", "Compte", domain="[('teneur','=',teneur),('fg_attente','=',True)]", required=True)
    libelle = fields.Char("Libellé", readonly=True)
    imput = fields.Integer("Imput")
    noecr = fields.Integer("Une ecriture ?")
    no_lecr = fields.Integer("Une ligne ?")
    sens = fields.Char("Sens", readonly=True)
    ligne_ids = fields.One2many("compta_envoi_ligne_gs_line", "envoi_ligne_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    teneur = fields.Many2one('compta_teneur_compte', string='Teneur de compte', domain="[('teneur','=', user_id)]", required=True)
    user_id = fields.Many2one('res.users', string='user', readonly=True,  default=lambda self: self.env.user)


class ComptaEnvoiLigneGSLine(models.Model):
    _name = "compta_envoi_ligne_gs_line" 
    
    envoi_ligne_id = fields.Many2one("compta_envoi_ligne_gs", ondelete='cascade')
    no_lecr = fields.Integer("N° Ligne", readonly=True)
    objet = fields.Char("Objet", readonly=True)
    sens = fields.Char("Sens", readonly=True)
    montant = fields.Integer("Montant", readonly=True)
    pj = fields.Char("PJ", readonly=True)
    etat = fields.Char("Etat", readonly=True)
    cocher = fields.Boolean("Cocher pour envoyer")


class ComptaBloquerCompte(models.Model):
    _name = "compta_bloquer_compte"
    
    name = fields.Char("nom", default="Blocage de compte")
    compte = fields.Many2one("compta_plan_line","Compte concerné",domain = [("fg_bloque", "=", False)])
    compte_d = fields.Many2one("compta_plan_line","Compte à débloquer", domain = [("fg_bloque", "=", True)])
    dte = fields.Date("Date de blocage",default=fields.Date.context_today, readonly=True)
    dte_d = fields.Date("Date de déblocage", readonly= True)
    motif = fields.Text("Motif du blocage")
    motif_d = fields.Text("Motif du déblocage")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    def bloquer(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_imput = int(self.compte.souscpte.id)
        
        self.env.cr.execute("""UPDATE compta_plan_line SET fg_bloque = True WHERE company_id = %d and x_exercice_id = %d and souscpte = %d
        """ %(v_struct, v_ex, v_imput ))
    
    def debloquer(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        v_imput_d = int(self.compte_d.souscpte.id)
        
        self.env.cr.execute("""UPDATE compta_plan_line SET fg_bloque = False WHERE company_id = %d and x_exercice_id = %d and souscpte = %d
        """ %(v_struct, v_ex, v_imput_d ))

class ComptaCloture(models.Model):
    _name = "compta_cloture"
    
    name = fields.Char("nom", default="Clôture de compte")
    compte = fields.Many2one("compta_plan_line","Compte", required = True)
    dte = fields.Date(default=fields.Date.context_today)
    debit = fields.Integer("Débit",readonly=True)
    credit = fields.Integer("Crédit",readonly=True)
    solde = fields.Integer("Solde",readonly=True)
    s_solde = fields.Char("Solde",readonly=True)
    cloture_line = fields.One2many("compta_cloture_line","cloture_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    
    def chercher(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        imput = int(self.compte.souscpte.id)
        v_id = int(self.id)
        
        
        for vals in self:
            vals.env.cr.execute("""select l.no_ecr as ecr, l.no_lecr as lecr, l.lb_lecr as lib, l.mt_lecr as mt, l .fg_sens as sens, l.fg_etat as etat from compta_ligne_ecriture l where l.company_id = %s and l.x_exercice_id = %s and
            l.no_souscptes = %s and l.fg_etat in ('V','W') order by l.no_ecr, l.no_lecr""" ,(val_struct,val_ex, imput))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.cloture_line.unlink()
            for line in rows:
                result.append((0,0, {'no_ecr' : line['ecr'], 'no_lecr': line['lecr'], 'libelle': line['lib'], 'montant': line['mt'], 'sens': line['sens'], 'etat': line['etat']}))
            self.cloture_line = result
        
        self.env.cr.execute("""select sum(montant) from compta_cloture_line l, compta_cloture c where c.id = l.cloture_id and l.cloture_id = %d and c.company_id = %d and
        c.x_exercice_id = %d and l.sens = 'C'""" %(v_id, val_struct, val_ex))
        vals = self.env.cr.fetchone()
        self.credit = vals and vals[0] or 0
        
        self.env.cr.execute("""select sum(montant) from compta_cloture_line l, compta_cloture c where c.id = l.cloture_id and l.cloture_id = %d and c.company_id = %d and
        c.x_exercice_id = %d and l.sens = 'D'""" %(v_id, val_struct, val_ex))
        val = self.env.cr.fetchone()
        self.debit = val and val[0] or 0
        
        if self.debit > self.credit:
            self.s_solde = "Solde débiteur"
        else:
            self.s_solde = "Solde créditeur"
        self.solde = self.debit - self.credit
    
    
    @api.onchange('compte')
    def verif_cloture(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        imput = int(self.compte.souscpte.id)
        
        if self.compte:
        
            self.env.cr.execute("""select fg_etat from compta_ligne_ecriture where company_id = %d and 
            x_exercice_id = %d and no_souscptes = %d""" %(val_struct, val_ex, imput))   
            val = self.env.cr.fetchone()
            vale = val and val[0] or 0  
            if vale == 'C':
                raise ValidationError(_("Désolé - Ce compte est déja clôturé"))
    
    def ecriture_fg(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        imput = int(self.compte.souscpte.id)
        dte = self.dte
    
        self.env.cr.execute("""select sum( case when l.fg_sens = 'D' then l.mt_lecr end) as debiteur,sum( case when l.fg_sens = 'C' then l.mt_lecr end) as crediteur 
        from compta_ligne_ecriture l where l.company_id = %d and l.x_exercice_id = %d and l.no_souscptes = %d 
        and l.no_ecr > 0 and l.fg_etat <> 'A' """ %(val_struct, val_ex, imput))
        res = self.env.cr.dictfetchall()
        mt_debit = res['debiteur']
        mt_credit = res['crediteur']
        
        self.env.cr.execute("select coalesce(max(no_ecr),0) + 1 from compta_ecriture_fg where x_exercice_id = %d and company_id = %d" ,(val_ex, val_struct))
        v_ecr = self.env.cr.fetchone()
        v_no_ecr = v_ecr and v_ecr[0] or 0  
        
        self.env.cr.execute("select coalesce(max(no_lecr),0) + 1 from compta_ligne_ecriture_fg where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct))
        v_lecr = self.env.cr.fetchone()
        v_no_lecr = v_lecr and v_lecr[0] or 0
          
        self.env.cr.execute("INSERT INTO compta_ecriture_fg(no_ecr, dt, x_exercice_id, company_id, etat) VALUES (%s, %s, %s, %s, 'N')" ,(v_no_ecr, dte, val_ex, val_struct))

        if mt_debit != 0:
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture_fg (x_exercice_id, company_id, no_ecr, no_lecr, mt_lecr, fg_sens, etat, dt_cre) 
            VALUES (%s, %s, %s, %s, %s 'D', 'N', %s) """ ,(val_ex, val_struct, v_no_ecr, v_no_lecr, mt_debit, dte))
        
        if mt_credit != 0:
            v_no_lecr = v_no_lecr + 1
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture_fg (x_exercice_id, company_id, no_ecr, no_lecr, mt_lecr, fg_sens, etat, dt_cre) 
            VALUES (%s, %s, %s, %s, %s 'C', 'N', %s) """ ,(val_ex, val_struct, v_no_ecr, v_no_lecr, mt_credit, dte))

            
    def balance_entree(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        imput = int(self.compte.souscpte.id)
        dte = self.dte
        
        self.env.cr.execute("""select count(*) from compta_ecriture_fg where x_exercice_id = %d and company_id = %d and no_ecr = 0""" %(val_ex, val_struct))
        fg = self.env.cr.fetchone()
        fg_exist = fg and fg[0] or 0
        
        self.env.cr.execute("""select
        coalesce(sum( case when l.fg_sens = 'D' then l.mt_lecr end),0) as debiteur,
        coalesce(sum( case when l.fg_sens = 'C' then l.mt_lecr end),0) as crediteur
        from ref_souscompte r, compta_plan_line c, compta_ligne_ecriture lwhere l.fg_etat != 'A' and l.no_ecr = 0 
        and r.id = l.no_souscptes and c.souscpte = l.no_souscptes and l.no_souscptes = %s
        and l.company_id = %s and l.x_exercice_id = %s """ ,(imput, val_struct, val_ex))
        res = self.env.cr.dictfetchall()
        mt_debit = res['debiteur']
        mt_credit = res['crediteur']
        
        
        v_no_ecr = 0
        if fg_exist == 0:
            self.env.cr.execute("""INSERT INTO compta_ecriture_fg(no_ecr, dt, x_exercice_id, company_id, etat) 
            VALUES (%s, %s, %s, %s, 'N')""" ,(v_no_ecr, dte, val_ex, val_struct))
            
        self.env.cr.execute("""SELECT coalesce(max(l.no_lecr),0) + 1 FROM compta_ligne_ecriture_fg l WHERE
        l.company_id = %s and l.x_exercice_id = %s""",(val_struct, val_ex))
        no_lecr  = self.env.cr.fetchone()
        v_no_lecr = no_lecr and no_lecr[0] or 0
        
        
        if mt_debit == 0:
            v_solde = mt_credit
            v_fg_sens = 'C'
        elif mt_credit == 0:
            v_solde = mt_debit
            v_fg_sens = 'D'
        elif mt_debit > mt_credit:
            v_solde = mt_debit - mt_credit
            v_fg_sens = 'D'
        elif mt_debit < mt_credit:
            v_solde = mt_credit - mt_debit
            v_fg_sens = 'C'
            
        if v_solde != 0: 
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture_fg (x_exercice_id, company_id, no_ecr, no_lecr, mt_lecr, fg_sens, etat, dt_cre) 
            VALUES (%s, %s, %s, %s, %s 'D', 'N', %s) """ ,(val_ex, val_struct, v_no_ecr, v_no_lecr, mt_debit, dte))
            v_no_lecr = v_no_lecr +1
            
            self.env.cr.execute("""INSERT INTO compta_ligne_ecriture_fg (x_exercice_id, company_id, no_ecr, no_lecr, mt_lecr, fg_sens, etat, dt_cre) 
            VALUES (%s, %s, %s, %s, %s 'C', 'N', %s) """ ,(val_ex, val_struct, v_no_ecr, v_no_lecr, mt_credit, dte))
            v_no_lecr = v_no_lecr +1
            
        
    def cloturer(self):
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        imput = int(self.compte.souscpte.id)
        
        #self.verif_cloture()
        self.env.cr.execute("""select count(fg_etat) from compta_ligne_ecriture where company_id = %d and 
        x_exercice_id = %d and no_souscptes = %d and fg_etat = "E" """ %(val_struct, val_ex, imput))   
        val = self.env.cr.fetchone()
        vale = val and val[0] or 0  
        if vale >= 1:
            raise ValidationError(_("Impossible de clôturer ce compte. Il existe toujours des lignes rejétées."))
        
        self.env.cr.execute("""select count(fg_etat) from compta_ligne_ecriture where company_id = %d and 
        x_exercice_id = %d and no_souscptes = %d and fg_etat = "P" """ %(val_struct, val_ex, imput))   
        val = self.env.cr.fetchone()
        vale = val and val[0] or 0  
        if vale >= 1:
            raise ValidationError(_("Impossible de clôturer ce compte. Il existe toujours des lignes provisoires."))
        
        deb = self.debit
        cred = self.credit
        
        self.env.cr.execute("select * from compta_compte_cloture where no_ex = %d and company_id = %d and compte = %d" %(val_ex, val_struct, imput))
        re = self.env.cr.fetchone()
        res = re and re[0] or 0
        if res == 1: 
            raise ValidationError(_("Ce compte est déja clôturé."))
        else:
            self.env.cr.execute("""insert into compta_compte_cloture (no_ex, company_id, compte, debit, credit, dt_clot, fg_etat)
            VALUES (%s, %s, %s, %s, %s, %s, 'C')""" ,(val_ex, val_struct, imput, deb, cred, dte))
    
        self.ecriture_fg()
        self.balance_entree()
        

class ComptaClotureLine(models.Model):
    _name = "compta_cloture_line"
    
    cloture_id = fields.Many2one("compta_cloture", ondelete="cascade")
    no_ecr = fields.Integer("N° Ecr", readonly=True)
    no_lecr = fields.Integer("N° Ligne", readonly=True)
    montant = fields.Integer("Montant", readonly=True)
    libelle = fields.Char("Libellé", readonly=True)
    etat = fields.Char("Etat", readonly=True)
    sens = fields.Char("Sens", readonly=True)
    dte = fields.Date("Date", readonly=True)


class CompteEtatCloture(models.Model):
    _name = "compta_etat_cloture"
    
    etat_cloture_line = fields.One2many("compta_etat_cloture_line","cloture_id")  
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaEtatClotureLine(models.Model):
    _name = "compta_etat_cloture_line"
    
    cloture_id = fields.Many2one("compta_etat_cloture", ondelete='cascade')
    compte = fields.Many2one("compta_plan_line","Compte", readonly=True)
    etat = fields.Char("Etat", readonly=True)
    dte_bloc = fields.Date("Date blocage", readonly=True)
    dte_clo = fields.Date("Date cloture", readonly=True)
    debit = fields.Integer("Débit (après cloture)",readonly=True)
    credit = fields.Integer("Crédit (après cloture)",readonly=True)
    

class ComptaEnvoiLigneLettre(models.Model):
    _name = "compta_envoi_ligne_lettre"
    _rec_name = "compte"

    compte = fields.Many2one("compta_plan_line",string="Compte",domain = [("fg_lettrage","=",True)])
    sens = fields.Selection([
        ('D', 'Débit'),
        ('C','Crédit'),
        ], string="Sens", required=True)
    ligne_lettre_line = fields.One2many("compta_envoi_ligne_lettre_line","envoi_ligne_lettre_id")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

class ComptaEnvoiLigneLettreLine(models.Model):
    _name = "compta_envoi_ligne_lettre_line"
    
    envoi_ligne_lettre_id = fields.Many2one("compta_envoi_ligne_lettre", ondelete='cascade')
    no_ecr = fields.Integer("N° Ecr", readonly=True)
    no_lecr = fields.Integer("N° Ligne", readonly=True)
    montant = fields.Integer("Montant", readonly=True)
    libelle = fields.Char("Libellé", readonly=True)
    etat = fields.Char("Etat", readonly=True)
    dte = fields.Date("Date", readonly=True)
    corriger = fields.Boolean("Corriger")


class ComptaCompteCloture(models.Model):
    _name = 'compta_compte_cloture'
    
    x_exercice_id = fields.Many2one("ref_exercice")
    company_id = fields.Many2one('res.company')
    compte = fields.Many2one("ref_souscompte")
    debit = fields.Integer()
    credit = fields.Integer()
    dt_bloc = fields.Date()
    dt_clot = fields.Date()


class ComptaEcritureFg(models.Model):
    _name = "compta_ecriture_fg"
    
    x_exercice_id = fields.Many2one("ref_exercice")
    company_id = fields.Many2one('res.company')
    no_ecr = fields.Integer()
    etat = fields.Char()
    dt = fields.Date()
    
    
class ComptaLigneEcritureFg(models.Model):
    _name = "compta_ligne_ecriture_fg"
    
    x_exercice_id = fields.Many2one("ref_exercice")
    company_id = fields.Many2one('res.company')
    no_ecr = fields.Integer()
    no_lecr = fields.Integer()
    mt_lecr = fields.Integer()
    fg_sens = fields.Char()
    dt_cre = fields.Date()
    etat = fields.Char()

class ComptaCompteResultat(models.TransientModel):
    _name = "compta_compte_resultat"
    
    name = fields.Many2one("compta_type_etat_financier",string="Libellé", default=lambda self: self.env['compta_type_etat_financier'].search([('cd_type_financier','=', 'CR')]), readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure", readonly=True)
    cr_ids = fields.One2many("compta_compte_resultat_line",'cr_id', readonly=True)
    
    def afficher(self):
        v_id = int(self.name)
        no_ex = int(self.x_exercice_id)
        struct = int(self.company_id)
        
        for vals in self:
            vals.env.cr.execute("""select cast(ordre as int) as ord, id as id_rub, cd_rubrique as refe, lb_long as lib, note as note, signe as signe from compta_rubrique_etat_financier 
            where type_etat = %d and company_id = %d order by ord asc""" %(v_id,struct))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.cr_ids.unlink()
            for line in rows:
                result.append((0,0, {'ord' : line['ord'],'id_rub' : line['id_rub'], 'ref' : line['refe'], 'libelle': line['lib'], 'note' : line['note'], 'signe': line['signe']}))
            self.cr_ids = result
        
        self.calcul()
        self.calculSum()
    
    def calcul(self):
        v_id = int(self.name)
        no_ex = int(self.x_exercice_id)
        struct = int(self.company_id)
        v_ids = int(self.id)
        v_exe = int(self.x_exercice_id.no_ex)
        v_exe1 = int(v_exe) - 1
        
        self.env.cr.execute("""select cast(ordr as int) as ord, lb_long as lib, existe as ext, formule as formule from compta_param_etat_financier where type_etat = %d and existe = 'N' order by ord""" %(v_id))
        for record in self.env.cr.dictfetchall():
            lib = record['lib']
            
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_plan_line cl, compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t
            where fl.cpte = cl.cpte and cl.souscpte = l.no_souscptes and t.id = p.type_etat and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and l.x_exercice_id = %d""" %(v_id, lib, struct, no_ex))
            mt = self.env.cr.fetchone()
            mnt = mt and mt[0] or 0
            self.env.cr.execute("UPDATE compta_compte_resultat_line SET exo_n = %d where id_rub = %d and cr_id = %d" %(mnt, lib, v_ids))
    
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_plan_line cl, compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t, ref_exercice r
            where fl.cpte = cl.cpte and cl.souscpte = l.no_souscptes and t.id = p.type_etat and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_id, lib, struct, v_exe1))
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_compte_resultat_line SET exo_n1 = %d where id_rub = %d and cr_id = %d" %(mnt1, lib, v_ids))
    
    

    def calculSum(self):
        v_id = int(self.name)
        no_ex = int(self.x_exercice_id)
        struct = int(self.company_id)
        v_ids = int(self.id)
        
        self.env.cr.execute("select distinct replace(formule,'+',':') as form, lb_long as lib from compta_param_etat_financier f where f.existe = 'Y' and type_etat = %d" %(v_id))
        for record in self.env.cr.dictfetchall():
            lib = record['lib']
            formu = record['form']
            formu1 = str(formu)
            formu2 = formu1.split(":")
            vari = tuple(formu2)
            
            self.env.cr.execute("select sum(l.exo_n) from compta_compte_resultat r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt = self.env.cr.fetchone()
            mnt = mt and mt[0] or 0
            self.env.cr.execute("UPDATE compta_compte_resultat_line SET exo_n = %d where id_rub = %d and cr_id = %d" %(mnt, lib, v_ids))           
            
            self.env.cr.execute("select sum(l.exo_n1) from compta_compte_resultat r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_compte_resultat_line SET exo_n1 = %d where id_rub = %d and cr_id = %d" %(mnt1, lib, v_ids))           
  
                
class ComptaCompteResultatLine(models.TransientModel):
    _name = "compta_compte_resultat_line"
    
    cr_id = fields.Many2one("compta_compte_resultat", ondelete='cascade')
    ord = fields.Integer("ord")
    id_rub = fields.Many2one("compta_rubrique_etat_financier")
    ref = fields.Char("REF", readonly=True)
    note = fields.Char("Note", readonly=True)
    signe = fields.Char(" ", readonly=True )
    libelle = fields.Char("LIBELLES", readonly=True)
    exo_n = fields.Integer("EXERCICE AU 31/12/N", readonly=True)
    exo_n1 = fields.Integer("EXERCICE AU 31/12/N-1", readonly=True)


class ComptaComptaBilan(models.TransientModel):
    _name = 'compta_bilan'
    
    name = fields.Many2one("compta_type_etat_financier",string="Libellé", default=lambda self: self.env['compta_type_etat_financier'].search([('cd_type_financier','=', 'BL')]), readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure", readonly=True)
    actif_ids = fields.One2many("compta_bilan_actif_line",'bl_id', readonly=True)
    passif_ids = fields.One2many("compta_bilan_passif_line",'bl_id', readonly=True)
    
    
    def afficher(self):
        v_id = int(self.name)
        no_ex = int(self.x_exercice_id)
        struct = int(self.company_id)
        
        for vals in self:
            vals.env.cr.execute("""select cast(ordre as int) as ord, id as id_rub, cd_rubrique as refe, lb_long as lib, note as note from compta_rubrique_etat_financier 
            where type_etat = %d and type_colonne = 1 order by ord asc""" %(v_id))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.actif_ids.unlink()
            for line in rows:
                result.append((0,0, {'ord' : line['ord'],'id_rub' : line['id_rub'], 'ref' : line['refe'], 'note': line['note'], 'actif': line['lib']}))
            self.actif_ids = result
            
        for vals in self:
            vals.env.cr.execute("""select cast(ordre as int) as ord, id as id_rub, cd_rubrique as refe, lb_long as lib, note as note from compta_rubrique_etat_financier 
            where type_etat = %d and type_colonne = 2 order by ord asc""" %(v_id))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.passif_ids.unlink()
            for line in rows:
                result.append((0,0, {'ord' : line['ord'],'id_rub' : line['id_rub'], 'ref' : line['refe'], 'note': line['note'], 'passif': line['lib']}))
            self.passif_ids = result
        
        self.calcul()
        self.calculSum()
    
    
    def calcul(self):
        v_id = int(self.name)
        no_ex = int(self.x_exercice_id)
        struct = int(self.company_id)
        v_ids = int(self.id)
        v_exe = int(self.x_exercice_id.no_ex)
        v_exe1 = int(v_exe) - 1
        
        self.env.cr.execute("""select cast(ordr as int) as ord, lb_long as lib, existe as ext, formule as formule from compta_param_etat_financier where type_etat = %d and existe = 'N' order by ord""" %(v_id))
        for record in self.env.cr.dictfetchall():
            lib = record['lib']
            
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_plan_line cl, compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t
            where fl.cpte = cl.cpte and cl.souscpte = l.no_souscptes and t.id = p.type_etat and p.type_categorie = '1' and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and l.x_exercice_id = %d""" %(v_id, lib, struct, no_ex))
            mt = self.env.cr.fetchone()
            mnt = mt and mt[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET brut = %d where id_rub = %d and bl_id = %d" %(mnt, lib, v_ids))
    
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_plan_line cl, compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t
            where fl.cpte = cl.cpte and cl.souscpte = l.no_souscptes and t.id = p.type_etat and p.type_categorie = '2' and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and l.x_exercice_id = %d""" %(v_id, lib, struct, no_ex))
            mt = self.env.cr.fetchone()
            mnt = mt and mt[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET amort = %d where id_rub = %d and bl_id = %d" %(mnt, lib, v_ids))
            
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_plan_line cl, compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t, ref_exercice r
            where fl.cpte = cl.cpte and cl.souscpte = l.no_souscptes and t.id = p.type_etat and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_id, lib, struct, v_exe1))
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET net_exo_n = %d where id_rub = %d and bl_id = %d" %(mnt1, lib, v_ids))
    
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_plan_line cl,compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t, ref_exercice r
            where fl.cpte = cl.cpte and cl.souscpte = l.no_souscptes and t.id = p.type_etat and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_id, lib, struct, v_exe1))
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET net_exo_n1 = %d where id_rub = %d and bl_id = %d" %(mnt1, lib, v_ids))
    
    
    
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t, ref_exercice r
            where fl.cptes = l.no_souscptes and t.id = p.type_etat and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_id, lib, struct, v_exe1))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_passif_line SET net_exo_n = %d where id_rub = %d and bl_id = %d" %(mnt1, lib, v_ids))
    
            self.env.cr.execute("""select sum(l.mt_lecr) as mnt from compta_ligne_ecriture l, compta_param_etat_financier_line fl, compta_param_etat_financier p, compta_type_etat_financier t, ref_exercice r
            where fl.cptes = l.no_souscptes and t.id = p.type_etat and fl.parametrage_id = p.id and t.id = %d and p.lb_long = %d and l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_id, lib, struct, v_exe1))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_passif_line SET net_exo_n1 = %d where id_rub = %d and bl_id = %d" %(mnt1, lib, v_ids))
    
    
    def calculSum(self):
        v_id = int(self.name)
        no_ex = int(self.x_exercice_id)
        struct = int(self.company_id)
        v_ids = int(self.id)
        
        self.env.cr.execute("select distinct replace(formule,'+',':') as form, lb_long as lib from compta_param_etat_financier f where f.existe = 'Y' and type_etat = %d" %(v_id))
        for record in self.env.cr.dictfetchall():
            lib = record['lib']
            formu = record['form']
            formu1 = str(formu)
            formu2 = formu1.split(":")
            vari = tuple(formu2)
            
            self.env.cr.execute("select sum(l.brut) from compta_bilan_actif_line r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt = self.env.cr.fetchone()
            mnt = mt and mt[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET brut = %d where id_rub = %d and cr_id = %d" %(mnt, lib, v_ids))           
            
            self.env.cr.execute("select sum(l.amort) from compta_bilan_actif_line r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET amort = %d where id_rub = %d and cr_id = %d" %(mnt1, lib, v_ids))           
  
            self.env.cr.execute("select sum(l.net_exo_n) from compta_bilan_actif_line r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET net_exo_n = %d where id_rub = %d and cr_id = %d" %(mnt1, lib, v_ids))           
  
            self.env.cr.execute("select sum(l.net_exo_n1) from compta_bilan_actif_line r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_actif_line SET net_exo_n1 = %d where id_rub = %d and cr_id = %d" %(mnt1, lib, v_ids))           
            
            
            self.env.cr.execute("select sum(l.net_exo_n1) from compta_bilan_passif_line r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_passif_line SET net_exo_n1 = %d where id_rub = %d and cr_id = %d" %(mnt1, lib, v_ids))           
  
  
            self.env.cr.execute("select sum(l.net_exo_n1) from compta_bilan_passif_line r, compta_compte_resultat_line l where ref in %s and r.id = l.cr_id and r.id = %s" %(vari, v_ids))        
            mt1 = self.env.cr.fetchone()
            mnt1 = mt1 and mt1[0] or 0
            self.env.cr.execute("UPDATE compta_bilan_passif_line SET net_exo_n1 = %d where id_rub = %d and cr_id = %d" %(mnt1, lib, v_ids))           
  

class ComptaCompteBilanActifLine(models.TransientModel):
    _name = "compta_bilan_actif_line"
    
    bl_id = fields.Many2one("compta_bilan", ondelete='cascade')
    ord = fields.Integer("ord")
    id_rub = fields.Many2one("compta_rubrique_etat_financier")
    ref = fields.Char("REF", readonly=True)
    vide = fields.Char("")
    note = fields.Char("Note", readonly=True)
    actif = fields.Char("ACTIF", readonly=True)
    brut = fields.Integer("BRUT", readonly=True)
    amort = fields.Integer("AMORT/DEPREC. ", readonly=True)
    net_exo_n = fields.Integer('NET au 31/12/N', readonly=True)
    net_exo_n1 = fields.Integer('NET au 31/12/N-1', readonly=True)


class ComptaCompteBilanPassifLine(models.TransientModel):
    _name = "compta_bilan_passif_line"
    
    bl_id = fields.Many2one("compta_bilan", ondelete='cascade')
    ord = fields.Integer("ord")
    id_rub = fields.Many2one("compta_rubrique_etat_financier")
    ref = fields.Char("REF", readonly=True)
    vide = fields.Char("")
    note = fields.Char("Note", readonly=True)
    passif = fields.Char("PASSIF", readonly=True)
    net_exo_n = fields.Integer("NET au 31/12/N", readonly=True)
    net_exo_n1 = fields.Integer('NET au 31/12/N-1', readonly=True)


class ComptaParamTva(models.Model):
    _name = "compta_param_tva"
    
    name = fields.Char(default="Taxe sur la Valeur Ajoutée")
    compte = fields.Many2one("compta_plan_line", "Compte TVA", required=True)
    compte_id = fields.Integer()
    taux = fields.Float("Taux TVA", default=18)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure", readonly=True)

    @api.onchange('compte')
    def Copte(self):
        if self.compte:
            self.compte_id = self.compte.souscpte


class SomTitre(models.Model):
    
    _name = "somtitre"
    _auto = False
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
   
    
    @api.model
    def init(self):
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        
        tools.drop_view_if_exists(self.env.cr, 'somtitre')
        self.env.cr.execute("""CREATE OR REPLACE VIEW somtitre AS
            select 
            distinct sum(l.mnts_budgetise) as montant, r.cd_titre as code, l.budg_id as budget from budg_ligne_budgetaire l, budg_titre t, ref_titre r 
            where r.id = t.titre and t.id = l.cd_titre_id and
            l.company_id = %d and l.x_exercice_id = %d group by code, budget order by code """ %(v_struct, v_ex))
    

class SomSection(models.Model):
    
    _name = "somsection"
    _auto = False
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice", readonly=True)
   
    @api.model
    def init(self):
        
        v_ex = int(self.x_exercice_id)
        v_struct = int(self.company_id)
        
        tools.drop_view_if_exists(self.env.cr, 'somsection')
        self.env.cr.execute("""CREATE OR REPLACE VIEW somsection AS
            select 
            distinct sum(l.mnts_budgetise) as montant, r.cd_section as code, l.budg_id as budget from budg_ligne_budgetaire l, budg_section s, ref_section r
            where r.id = s.section and s.id = l.cd_section_id and
            l.company_id = %d and l.x_exercice_id = %d group by code, budget order by code """  %(v_struct, v_ex))
    
"""
class RecepBal(models.Model):
    _name = "compta_reception_balance" 
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    lines = fields.One2many("compta_reception_balance_line")


class ReceptBalLine(models.Model):
    _name = "compta_reception_balance_line"
    
    entier_cpte = fields.Integer()
    numero_compte = fields.Char("N° et Intitulé de Compte")
    crediteur = fields.Integer("Créditeur")
    debiteur = fields.Integer("Débiteur")
    periode = fields.Many2one("compta_periode", string="Période")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
"""


class ComptaConsultation(models.Model):
    _name = 'compta_consultation'
    _rec_name = 'guichetier'

    guichetier = fields.Many2one("compta_caisse_struct", domain="[('cd_us_caisse','=', user_id)]", string="Guichetier",
                                 required=True)
    user_id = fields.Many2one('res.users', string='Caissier', default=lambda self: self.env.user)
    dte = fields.Date("Date debut")
    dte_fi  = fields.Date("Date fin")
    cheq = fields.Boolean("Tous Chèques")
    modreg = fields.Many2one("compta_jr_modreg", "Mode Règlement")
    tous = fields.Boolean("Tous les jours ouverts")
    total = fields.Float("Montant total")
    ferme_guichet_line = fields.One2many('compta_consultation_operation_line', 'consultation_id', readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice",string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    def action_afficher(self):

        val_ex = int(self.user_id.x_exercice_id)
        val_struct = int(self.company_id)
        v_id = int(self.guichetier.cd_us_caisse)
        v_jr = self.dte
        v_jr_fin = self.dte_fi
        v_reg = int(self.modreg)

        for val in self.ferme_guichet_line:
            val.x_exercice_id = val_ex


        if self.guichetier:
            if self.dte != False and self.dte_fi != False:
                if self.modreg:
                    for vals in self:
                        vals.env.cr.execute(""" select u.date_ope as dte, l.type1 as cat,l.type2 as typ2, u.factures as piece, u.numero as refe, u.ref_f as ref_f, u.mode_reglement as reg, u.nom_usager as nom, l.x_exercice_id as anne, l.id_imput as compte,
                                   case when u.type_operation = 1 then l.mnt_op_cpta end as encaisse,case when u.type_operation = 2 then l.mnt_op_cpta end as decaisse, l.fg_etat as etat
                                   from compta_guichet_line l, compta_guichet_unique u
                                   where u.id = l.guichet_id and l.x_exercice_id = %s and u.date_ope between '%s' and '%s' and u.mode_reglement = %s and l.company_id = %s and u.gui_us = %s and l.fg_etat not in ('A')
                                   order by u.date_ope""" %(val_ex, v_jr, v_jr_fin, v_reg, val_struct, v_id))
                        rows = vals.env.cr.dictfetchall()
                        result = []

                        vals.ferme_guichet_line.unlink()
                        for line in rows:
                            result.append((0, 0, {'dte': line['dte'], 'categop': line['cat'], 'typeop': line['typ2'],
                                                  'typepiece': line['piece'],
                                                  'refp': line['refe'],'ref_f': line['ref_f'], 'modreg': line['reg'], 'intervenant': line['nom'],
                                                  'annee': line['anne'], 'mt_encaisse': line['encaisse'],
                                                  'mt_decaisse': line['decaisse'],'etat': line['etat']}))
                        self.ferme_guichet_line = result

                elif self.cheq == True:
                    for vals in self:
                        vals.env.cr.execute(""" select u.date_ope as dte, l.type1 as cat,l.type2 as typ2, u.factures as piece, u.numero as refe,u.ref_f as ref_f, u.mode_reglement as reg, u.nom_usager as nom, l.x_exercice_id as anne, l.id_imput as compte,
                                   case when u.type_operation = 1 then l.mnt_op_cpta end as encaisse,case when u.type_operation = 2 then l.mnt_op_cpta end as decaisse, l.fg_etat as etat
                                   from compta_guichet_line l, compta_guichet_unique u
                                   where u.id = l.guichet_id and l.x_exercice_id = %s and u.date_ope between '%s' and '%s' and u.modreg <> '0' and l.company_id = %s and u.gui_us = %s and l.fg_etat not in ('A')
                                   order by u.date_ope""" %(val_ex, v_jr, v_jr_fin, val_struct, v_id))
                        rows = vals.env.cr.dictfetchall()
                        result = []

                        vals.ferme_guichet_line.unlink()
                        for line in rows:
                            result.append((0, 0, {'dte': line['dte'], 'categop': line['cat'], 'typeop': line['typ2'],
                                                  'typepiece': line['piece'],
                                                  'refp': line['refe'],'ref_f': line['ref_f'], 'modreg': line['reg'], 'intervenant': line['nom'],
                                                  'annee': line['anne'], 'mt_encaisse': line['encaisse'],
                                                  'mt_decaisse': line['decaisse'],'etat': line['etat']}))
                        self.ferme_guichet_line = result

                else:
                    for vals in self:
                        vals.env.cr.execute(""" select u.date_ope as dte, l.type1 as cat,l.type2 as typ2, u.factures as piece, u.numero as refe,u.ref_f as ref_f, u.mode_reglement as reg, u.nom_usager as nom, l.x_exercice_id as anne, l.id_imput as compte,
                                   case when u.type_operation = 1 then l.mnt_op_cpta end as encaisse,case when u.type_operation = 2 then l.mnt_op_cpta end as decaisse, l.fg_etat as etat
                                   from compta_guichet_line l, compta_guichet_unique u
                                   where u.id = l.guichet_id and l.x_exercice_id = %s and u.date_ope between '%s' and '%s' and u.modreg in ('0','1','2') and l.company_id = %s and u.gui_us = %s and l.fg_etat not in ('A')
                                   order by u.date_ope""" %(val_ex, v_jr, v_jr_fin, val_struct, v_id))
                        rows = vals.env.cr.dictfetchall()
                        result = []

                        vals.ferme_guichet_line.unlink()
                        for line in rows:
                            result.append((0, 0, {'dte': line['dte'], 'categop': line['cat'], 'typeop': line['typ2'],
                                                  'typepiece': line['piece'],
                                                  'refp': line['refe'],'ref_f': line['ref_f'], 'modreg': line['reg'], 'intervenant': line['nom'],
                                                  'annee': line['anne'], 'mt_encaisse': line['encaisse'],
                                                  'mt_decaisse': line['decaisse'],'etat': line['etat']}))
                        self.ferme_guichet_line = result

            elif self.dte:
                if self.modreg:
                    for vals in self:
                        vals.env.cr.execute(""" select u.date_ope as dte, l.type1 as cat,l.type2 as typ2, u.factures as piece, u.numero as refe,u.ref_f as ref_f, u.mode_reglement as reg, u.nom_usager as nom, l.x_exercice_id as anne, l.id_imput as compte,
                                   case when u.type_operation = 1 then l.mnt_op_cpta end as encaisse,case when u.type_operation = 2 then l.mnt_op_cpta end as decaisse, l.fg_etat as etat
                                   from compta_guichet_line l, compta_guichet_unique u
                                   where u.id = l.guichet_id and l.x_exercice_id = %s and u.date_ope = '%s' and u.mode_reglement = %s and l.company_id = %s and u.gui_us = %s and l.fg_etat not in ('A')
                                   order by u.date_ope""" %(val_ex, v_jr, v_reg, val_struct, v_id))
                        rows = vals.env.cr.dictfetchall()
                        result = []

                        vals.ferme_guichet_line.unlink()
                        for line in rows:
                            result.append((0, 0, {'dte': line['dte'], 'categop': line['cat'], 'typeop': line['typ2'],
                                                  'typepiece': line['piece'],
                                                  'refp': line['refe'],'ref_f': line['ref_f'], 'modreg': line['reg'], 'intervenant': line['nom'],
                                                  'annee': line['anne'], 'mt_encaisse': line['encaisse'],
                                                  'mt_decaisse': line['decaisse'],'etat': line['decaisse'],'etat': line['etat']}))
                        self.ferme_guichet_line = result
                elif self.cheq == True:
                    for vals in self:
                        vals.env.cr.execute(""" select u.date_ope as dte, l.type1 as cat,l.type2 as typ2, u.factures as piece, u.numero as refe,u.ref_f as ref_f, u.mode_reglement as reg, u.nom_usager as nom, l.x_exercice_id as anne, l.id_imput as compte,
                                   case when u.type_operation = 1 then l.mnt_op_cpta end as encaisse,case when u.type_operation = 2 then l.mnt_op_cpta end as decaisse, l.fg_etat as etat
                                   from compta_guichet_line l, compta_guichet_unique u
                                   where u.id = l.guichet_id and l.x_exercice_id = %s and u.date_ope = '%s' and u.modreg <> '0' and l.company_id = %s and u.gui_us = %s and l.fg_etat not in ('A')
                                   order by u.date_ope""" %(val_ex, v_jr, val_struct, v_id))
                        rows = vals.env.cr.dictfetchall()
                        result = []

                        vals.ferme_guichet_line.unlink()
                        for line in rows:
                            result.append((0, 0, {'dte': line['dte'], 'categop': line['cat'], 'typeop': line['typ2'],
                                                  'typepiece': line['piece'],
                                                  'refp': line['refe'], 'ref_f': line['ref_f'], 'modreg': line['reg'], 'intervenant': line['nom'],
                                                  'annee': line['anne'], 'mt_encaisse': line['encaisse'],
                                                  'mt_decaisse': line['decaisse'],'mt_decaisse': line['decaisse'],'mt_decaisse': line['decaisse'],'etat': line['etat']}))
                        self.ferme_guichet_line = result





class ComptaConsultationOpLine(models.Model):
    _name = 'compta_consultation_operation_line'

    consultation_id = fields.Many2one('compta_consultation', ondelete='cascade')
    dte = fields.Date("Date")
    categop = fields.Many2one("compta_operation_guichet", "Catégorie opération")
    typeop = fields.Many2one("compta_type_op_cpta", "Type opération")
    natdet = fields.Char('Nature détaillée')
    intervenant = fields.Char("Client")
    modreg = fields.Many2one("compta_jr_modreg", "Mode Reg.")
    typepiece = fields.Char("Ref. facture")
    ref_f = fields.Char("Ref. facture(2022)")
    refp = fields.Char('Ref. Chèque')
    annee = fields.Many2one("ref_exercice", 'Année')
    mt_encaisse = fields.Integer('Montant encaissé')
    mt_decaisse = fields.Integer('Montant décaissé')
    x_exercice_id = fields.Many2one("ref_exercice",
                                    default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),
                                    string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    etat = fields.Char("Etat")


class ComptaAnnulationFacture(models.Model):
    _name = "compta_annulation_facture"
    _rec_name = "num_facture"

    num_facture = fields.Many2one("compta_facturation", "N° Facture", required=True)
    montant = fields.Float("Montant")
    state = fields.Selection([('N','Annulation en cours'),('A','Annulé')],default='N', string="Etat")

    @api.onchange('num_facture')
    def mt(self):
        if self.num_facture:
            self.montant = self.num_facture.ttc
    
    def annuler(self):
        num = int(self.num_facture)
        mt = self.montant
        for val in self:
            self.env.cr.execute("update compta_facturation set etat = 'A' where id = %d" %(v_id))
            self.state = 'A'

    def restaurer(self):
        num = int(self.num_facture)
        mt = self.montant
        for val in self:
            self.env.cr.execute("update compta_facturation set etat = 'V', reste = %s where id = %s" ,(mt, v_id))
            self.state = 'A'
