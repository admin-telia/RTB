from odoo import api, models, fields, _
from datetime import date
from odoo.exceptions import UserError, ValidationError
from num2words import num2words
import qrcode
import base64
from io import BytesIO


class ComptaModeReg(models.Model):
    _name = "compta_mode_regularisation"
    
    lb_court = fields.Char("Libellé court")
    name = fields.Char("Libellé long", required=True)

class Compta_Type1OpCpta(models.Model):
    
    _name = 'compta_type1_op_cpta'
    _rec_name = 'lb_long' 
    
    type1_opcpta = fields.Char("Code", size =3, required=True)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65, required=True)
    data_id = fields.Many2one("compta_data", "Type opération")
    active = fields.Boolean('Actif',default=True)
    
  
class Compta_TypeOpCptaline(models.Model):
    
    _name = 'compta_type_op_cpta_line'
    _rec_name = 'type1_opcpta'
    
    type1_opcpta = fields.Many2one("compta_type1_op_cpta", "Libellé de type de base")
    type_opguichet_ids = fields.One2many('compta_type_op_cpta','type_opcpta_id')  
    
    
    
class Compta_TypeOpCpta(models.Model):
    
    _name = 'compta_type_op_cpta'
    
    #type1_opcpta usage pour enregistrememnt unique à enlever si solution groupée trouvée
    reg_op_guichet = fields.Many2one("compta_reg_op_guichet")
    type1_opcpta = fields.Many2one("compta_type1_op_cpta", "Libellé de type de base")
    type_opcpta_id = fields.Many2one("compta_type_op_cpta_line")
    type_opcpta1 = fields.Char("Code", size =5, required=True)
    lb_court = fields.Char("Libellé court", size=50)
    name = fields.Char("Libellé ", required=True)
    fg_pc = fields.Selection([
        ('S', 'Sans'),
        ('P', 'Préalable'),
        ('R', 'Regul'),
        ('I', 'Immédiat'),
        ('U', 'Ultérieur'),
        ('?', '?'),
        ], ' ', default='S', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    fg_term = fields.Selection([
        ('T', 'Y-Terminal'),
        ('N', 'N-Non (ici)'),
        ('L', 'L-Non(Lv)'),
        ], 'Niveau de determination', default='T', required=True)
    col_id = fields.Many2one('compta_colonne_caisse', "Col. brouill caiss",required=True)
    no_imputation = fields.Many2one("compta_plan_line", 'Imputation')
    souscompte_id = fields.Integer()
    list_val = fields.Many2one("compta_table_listnat", 'Nature détaillée')
    no_imp_pc = fields.Char('       ',size=10)
    lb_nature = fields.Char('           ',size=15)
    fg_grant_ac = fields.Boolean("Ac")
    fg_grant_ord = fields.Boolean("ORD")
    fg_facial = fields.Boolean()
    fg_guichet = fields.Boolean("Gui.")
    fg_ch_emis = fields.Boolean("Cheq./Vir.")
    fg_op_relev = fields.Boolean("Rel.")
    fg_retenue = fields.Boolean("Ret.")
    typ2_assign = fields.Char(size=3)
    na_fixe = fields.Char(size=10)
    typebase_id = fields.Many2one("compta_operation_guichet", ondelete='cascade')
    regle_id = fields.Many2one("compta_regle_operation_guichet")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    
    
    @api.onchange('no_imputation')
    def Val_Imput(self):
        for x in self:
            x.souscompte_id = x.no_imputation.souscpte.id
    
class Compta_TypeColonneCaisse(models.Model):
    
    _name = 'compta_colonne_caisse'
    _rec_name = 'lb_long'
    
    cd_col_caise = fields.Char("Code", size =3)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65, required=True)
    active = fields.Boolean('Actif',default=True) 
    #test = fields.Selection(selection = 'function_test')   
    
    _sql_constraints = [
        ('cd_col_caise', 'unique (cd_col_caise)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
    
    """
    @api.model
    def function_test(self):
        nom_vue = str('vue_nature')
        clause_w = str('cd_nat = 2')
        
        #nature = self.env['compta_colonne_caisse'].search([])
        #return [(x.cd_col_caise, x.lb_court) for x in nature]
    
        #self.env.cr.execute("select * from %s where %s" %(nom_vue,clause_w))
        nature = self.env['vue_nature'].search([])
        #nature = self.env.cr.dictfetchall()
        return [(x.cd_nat, x.lb_nat) for x in nature]
        print('valeur nature',nature)
    """
    
class Compta_TypeOpBanque(models.Model):
    
    _name='compta_type_op_banque'
    _rec_name = 'lb_long'
  
  
    #type1_opcpta_id usage pour enregistrememnt unique à enlever si solution groupée trouvée
    reg_op_banque = fields.Many2one("compta_reg_op_banque")
    type1_opcpta = fields.Many2one("compta_type_op_banque_line")
    type_opbq = fields.Char("Code",size=5)
    lb_court = fields.Char("Libellé court", size=50)
    lb_long = fields.Char("Libellé long", size=100)
    lb_comment = fields.Char('Commentaire',size=200)
    no_cpt_deb = fields.Many2one('compta_plan_line', 'Débit')
    no_cpt_cred = fields.Many2one('compta_plan_line', 'Crédit')
    cpte_cred = fields.Integer()
    cpte_deb = fields.Integer()
    type_journal_id = fields.Many2one('compta_type_journal', "Type de journal")
    cd_assign = fields.Selection([
        ('ac', 'AC'),
        ('daf', 'DAF'),
        ('struct', 'STRUCT'),
        ], 'Assignataire', index=True, copy=False, track_visibility='always')
    typebase_id = fields.Many2one("compta_operation_banque", ondelete='cascade')
    regle_id = fields.Many2one("compta_regle_operation_banque")
    
    @api.onchange('no_cpt_deb')
    def deb(self):
        if self.no_cpt_deb:
            self.cpte_deb = self.no_cpt_deb.souscpte.id

    @api.onchange('no_cpt_cred')
    def cred(self):
        if self.no_cpt_cred:
            self.cpte_cred = self.no_cpt_cred.souscpte.id

    
class Compta_TypeOpBanqueline(models.Model):
    
    _name = 'compta_type_op_banque_line'
    _rec_name = 'type1_opcpta_id'
    
    type1_opcpta_id = fields.Many2one("compta_type1_op_cpta", "Libellé de type de base")
    type_opbq_ids = fields.One2many('compta_type_op_banque','type1_opcpta')
    
    
class Compta_type_ecriture(models.Model): 
    
    _name='compta_type_ecriture'
    _rec_name = 'lb_long'
    
    type_ecriture = fields.Char("Code", size =1, required=True)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65, required=True)
    active = fields.Boolean('Actif',default=True)

    _sql_constraints = [
        ('type_ecriture', 'unique (type_ecriture)', "Ce code existe déjà. Veuillez changer de code !"),
    ]  
    

class Compta_type_op_ecriture(models.Model): 
    
    _name='compta_type_op_ecriture'
    _rec_name = 'lb_long'
    
    type_op_ecr = fields.Char("Code", size =2)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65)
    active = fields.Boolean('Actif',default=True)

    _sql_constraints = [
        ('type_op_ecr', 'unique (type_op_ecr)', "Ce code existe déjà. Veuillez changer de code !"),
    ] 
    

class Compta_TypeLbLecriture(models.Model):
    
    _name = 'compta_typelblecriture'
    _rec_name = 'lb_long'
    
    type_lblecriture = fields.Char("Code", size =1)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65)
    active = fields.Boolean('Actif',default=True)
    
    _sql_constraints = [
        ('type_lblecriture', 'unique (type_lblecriture)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
    
    
class Compta_TypeJournal(models.Model):
    
    _name='compta_type_journal'
    _rec_name = 'lb_long'
    
    
    type_journal = fields.Char("Code", size =5, required=True)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65, required=True)
    active = fields.Boolean('Actif',default=True)
    
    _sql_constraints = [
        ('type_journal', 'unique (type_journal)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
    

class Compta_TypeQuittance(models.Model):

    _name = "compta_type_quittance"
    _rec_name = 'lb_long'
    
    ty_quittance = fields.Char("Code")
    lb_long = fields.Char("Libellé court",size = 65)
    lb_court = fields.Char("Libellé long",size=35, required=True)
    active = fields.Boolean('Actif',default=True)
    
    _sql_constraints = [
        ('ty_quittance', 'unique (ty_quittance)', "Ce code existe déjà. Veuillez changer de code !"),
        
    ]
    
class Compta_TypeBilletage(models.Model):

    _name = "compta_type_billetage"
    _rec_name = 'lb_long'
    
    type_billetage = fields.Char("Code")
    lb_long = fields.Char("Libellé court",size = 65)
    lb_court = fields.Char("Libellé long",size=35)
    active = fields.Boolean('Actif',default=True)
    
    _sql_constraints = [
        ('type_billetage', 'unique (type_billetage)', "Ce code existe déjà. Veuillez changer de code !"),
        
    ]
    
    
class Compta_TypePeriode(models.Model):

    _name = "compta_type_periode"
    _rec_name = 'lb_long'
    
    ty_periode = fields.Char("Code")
    lb_long = fields.Char("Libellé long" ,size = 65)
    lb_court = fields.Char("Libellé court" ,size=35)
    active = fields.Boolean('Actif',default=True)


class Compta_Periode(models.Model):
    _name = 'compta_periode'
    _rec_name = 'lb_periode'
    
    cd_type = fields.Many2one("compta_type_periode", 'Type de période',states={'O': [('readonly', True)]}, required=True)
    dt_debut = fields.Date("Date de début", required=True, states={'O': [('readonly', True)],'F': [('readonly', True)]})
    dt_fin = fields.Date("Date de fin",required=True,states={'O': [('readonly', True)]})
    lb_periode = fields.Char("Libellé",required=True,states={'O': [('readonly', True)]})
    numero = fields.Integer("N°",states={'O': [('readonly', True)]})
    active = fields.Boolean('Actif',default=True)
    state = fields.Selection([
        ('draft','Brouillon'),
        ('O','Ouverte'),
        ('A','Arrêtée'),
        ('F','Clotûrée'),
        ], string="Etat", default="draft")

    
    def ouvrir(self):
        self.write({'state': 'O'})
    
    @api.onchange('dt_fin')
    def OnChangeDate(self):
        val_date = date.today()
        
        if self.dt_fin < self.dt_debut:
            raise ValidationError(_('Vérifiez les date'))
        
        #if self.dt_fin > val_date:
            #self.active = False

class Compta_TypeIntervExt(models.Model):
    
    _name = 'compta_type_interv_ext'
    _rec_name = 'lb_long'
    
    type_ivext = fields.Char('Code', size=4)
    lb_court = fields.Char("Libellé court", size=35)
    lb_long = fields.Char("Libellé long", size=65, required=True)
    fg_enc = fields.Boolean()
    fg_dec = fields.Boolean()
    nm_table = fields.Char(size=20)
    ls_col_table = fields.Char(size=50)
    active = fields.Boolean('Actif',default=True)
    
    _sql_constraints = [
        ('type_ivext', 'unique (type_ivext)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
    
class Compta_intervant(models.Model):
    
    _name = "compta_intervenant"
    
    type_op = fields.Many2one("compta_reg_op_guichet_unique", string ="Type d'opération")
    intervenant_id = fields.Many2one("compta_type_interv_ext", string="Libellé usager")
    
class Budg_TypeBordTrans(models.Model):
    
    _inherit = "budg_typebordtrans"
    
    fictif = fields.Char("fictif")
    
    
class Compta_teneur(models.Model):
    _name = 'compta_teneur_cpte'
    _rec_name="no_cpte"
    
    user_id = fields.Many2one('res.users', string='Teneur', required=True)
    no_cpte = fields.Many2one("compta_plan_line", "Compte", required=True)
    active = fields.Boolean('Actif',default=True)
    fg_sens = fields.Char("Sens")
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class ComptaOperationGuichet(models.Model):
    _name = "compta_operation_guichet"
    _rec_name = "typebase"
    
    data_id = fields.Many2one('compta_data')
    typebase = fields.Many2one("compta_type1_op_cpta", "Opération de base", required=True)
    code = fields.Char("Code", readonly=True)
    operation_guichet_ids = fields.One2many("compta_type_op_cpta", "typebase_id")
    
    @api.onchange('typebase')
    def Code(self):
        if self.typebase:
            self.code = self.typebase.type1_opcpta
            

class ComptaOperationBanque(models.Model):
    _name = "compta_operation_banque"
    _rec_name = "typebase"
    
    typebase = fields.Many2one("compta_type1_op_cpta", "Type de base", required=True)
    code = fields.Char("Code", readonly=True)
    operation_banque_ids = fields.One2many("compta_type_op_banque","typebase_id")
    
    @api.onchange('typebase')
    def Code(self):
        if self.typebase:
            self.code = self.typebase.type1_opcpta


class Categorie(models.Model):
    _name = 'compta_categorie'
    
    code = fields.Char("Code", size=5)
    lb_court = fields.Char("Libellé court")
    name = fields.Char("Libellé", required=True)
    
    
class TypePrestation(models.Model):
    _name = 'compta_type_prestation'
    
    code = fields.Char("Code", size=5)
    lb_court = fields.Char("Libellé court", required=False)
    name = fields.Char("Libellé", required=True)


class Prestation(models.Model):
    _name = 'compta_prestation'
    
    code = fields.Char("Code", size=5)
    lb_court = fields.Char("Libellé court", required=False)
    name = fields.Char("Libellé", required=True)



class Parametre(models.Model):
    _name = "compta_parametre"
    _rec_name = 'designation'
    
    categorie_id = fields.Many2one("compta_categorie", "Catégorie de prestation", required=True)
    type_id = fields.Many2one("compta_type_prestation", "Type de prestation", required=True)
    designation = fields.Many2one("compta_prestation", "Prestation", required=True)
    support = fields.Selection([("tv","Télé"),("radio","Radio")], string="Support de diffusion")
    rtb = fields.Selection([("1","RTB1"),("2","RTB2")], string="Choisir le")
    horaire = fields.Many2one("compta_horaire", "Horaire")
    localite = fields.Many2one("ref_localite", "Localité")
    duree = fields.Integer("Durée (en seconde)")
    prix_unitaire = fields.Integer("Coût", required=True)

class Horaire(models.Model):
    _name = "compta_horaire"
    
    name = fields.Char("Libellé", required=True)
    code = fields.Char("Code")

    

class FacturationProf(models.Model):
    _name = "compta_facturation_prof"
    _rec_name = "num_facture"
    
    client_id = fields.Many2one("ref_contribuable", "DOIT :", required=True)
    telephone = fields.Char("Téléphone", readonly=False)
    num_facture = fields.Char("Facture N°", readonly=True)
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    dte = fields.Date("Date", default=fields.Date.context_today)
    objet = fields.Text("Objet", required=True)
    ht = fields.Integer("Montant Total sans remise", readonly=True)
    remise = fields.Integer("Remise", compute='_compute_amount')
    total_ht = fields.Integer("Montant HT", compute='_calcul_total_ht')
    tva = fields.Integer("TVA (18%)", readonly=True, compute='_calcul_total_ht')
    tvaex = fields.Boolean("TVA ?")
    ttc = fields.Integer("Montant TTC", readonly=True, compute='_calcul_total_ht')
    structure_id = fields.Many2one('compta_structure','Structure', required=True)
    state = fields.Selection([('N','Nouvelle'),('P','Proforma'),('T','Validé')],default='N',string="Etat")
    facture_ids = fields.One2many("compta_facturation_ligne","facture_id")
    signataire_dcm = fields.Many2one("budg_signataire", default=lambda self: self.env['budg_signataire'].search([('code','=', 'DCM')]))
    signataire_csc = fields.Many2one("budg_signataire", default=lambda self: self.env['budg_signataire'].search([('code','=', 'CSC')]))
    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )

    current_users = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)

    @api.onchange('current_users')
    def User(self):
        if self.current_users:
            self.x_exercice_id = self.current_users.x_exercice_id

    """@api.constrains('x_exercice_id')
    def _ControleExercice(self):
        no_ex = int(self.x_exercice_id)
        v_ex = int(self.x_exercice_id.no_ex)
        for record in self:
            record.env.cr.execute("select count(id) from ref_exercice where etat = 1 and id = %d" % (no_ex))
            res = self.env.cr.fetchone()
            val = res and res[0] or 0
            if val == 0:
                raise ValidationError(_("Exercice" + " " + str(v_ex) + " " + "est clôs. Traitement impossible"))"""



    @api.depends('ttc')
    def amount_to_words(self):
        self.text_amount = num2words(self.ttc, lang='fr')

    
    def calculer(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        id_ordre = self.id
        
        for val in self:
        
            val.env.cr.execute("""SELECT sum(l.prix_total)
            FROM compta_facturation_ligne l, compta_facturation_prof f WHERE 
            f.company_id = %d AND l.facture_id = %d and f.id = l.facture_id """ %( val_struct, id_ordre))
            res = val.env.cr.fetchone()
            val_mnt = res and res[0] or 0

            val.ht = val_mnt

            #self.tva = round(self.ht * 0.18)
            #self.ttc = self.ht + self.tva
        #else:
            #self.ttc = val_mnt

    @api.onchange('client_id')
    def tele(self):
        for x in self:
            x.telephone = x.client_id.tel

    @api.one
    @api.depends('facture_ids.mnt_remise')
    def _compute_amount(self):

        self.remise = sum(line.mnt_remise for line in self.facture_ids)
    
    @api.depends('ht')
    def _calcul_total_ht(self):
        for x in self:
            x.total_ht = x.ht - x.remise
            if x.tvaex == True:
                x.tva = round(x.total_ht * 0.18)
                x.ttc = x.total_ht + x.tva
            else:
                x.tva = 0
                x.ttc = x.total_ht

            
        
        

    def valider(self):

        v_ex = int(self.current_users.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        for record in self:
        
            record.env.cr.execute("select nopro from compteur_pro where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct) )
            eng = record.env.cr.fetchone()
            no_eng = eng and eng[0] or 0
            c1 = int(no_eng) + 1
            c = str(no_eng)
            if c == "0":
                ok =str(c1).zfill(5)
                record.num_facture = ok
                vals = c1
                record.env.cr.execute("""INSERT INTO compteur_pro(x_exercice_id,company_id,nopro)  VALUES(%d ,%d, %d)""" %(val_ex, val_struct,vals))    
            else:
                c1 = int(no_eng) + 1
                c = str(no_eng)
                ok =str(c1).zfill(5)
                record.num_facture = ok
                vals = c1
                record.env.cr.execute("UPDATE compteur_pro SET nopro = %d WHERE x_exercice_id = %d and company_id = %d" %(vals, val_ex, val_struct))

        for v in self.facture_ids:
            v.x_exercice_id = val_ex
    
            record.write({'state': 'P'})
    


class FacturationLigne(models.Model):
    _name = "compta_facturation_ligne"
    
    facture_id = fields.Many2one("compta_facturation_prof", ondelete='cascade')
    facture_id_def = fields.Many2one("compta_facturation")
    facture_id_paie = fields.Many2one("compta_facturation_def")
    type1 = fields.Many2one("compta_operation_guichet", string="Catégorie d'opération", default=lambda self: self.env['compta_operation_guichet'].search([('code', '=', 'E00')]), required=True, readonly=True)
    type2 = fields.Many2one("compta_type_op_cpta", string="Nature de prestation", domain="[('typebase_id','=',type1), ('fg_guichet','=',True)]", required=True)
    qte = fields.Integer("Qté", default=1, required=True)
    id_imput = fields.Integer()
    id_imput_tva = fields.Integer()
    code2 = fields.Char()
    prix_unitaire = fields.Integer("Prix Unitaire", required=True)
    prix_remise = fields.Integer("Mt Remise", required=False)
    mnt_remise = fields.Integer("Mt remise", required=False)
    prix_total = fields.Integer("Montant",readonly=True)
    prix = fields.Integer("Total",readonly=True)
    tva = fields.Integer("TVA", readonly=False)
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    @api.onchange('type2')
    def Cod2(self):
        for val in self:
            if val.type2:
                val.code2 = val.type2.type_opcpta1
  
    
    @api.onchange("prix_unitaire","mnt_remise","qte")
    def Onchangeparam(self):
        
        for x in self:
            if x.mnt_remise != 0:
                x.prix_total = x.prix_unitaire * x.qte
                x.prix = x.prix_total - x.mnt_remise
            else:
                x.prix_total = x.prix_unitaire * x.qte
                x.prix = x.prix_total
    
    
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
            self.id_imput = imput and imput[0]["souscompte_id"]
            

class Facturation(models.Model):
    _name = "compta_facturation"
    _rec_name = "num_facture"
    
    client_id = fields.Many2one("ref_contribuable", "DOIT :", readonly=True)
    telephone = fields.Char("Téléphone", readonly=True)
    num_facture = fields.Char("Facture N°", readonly=True)
    num_facture_prof = fields.Many2one("compta_facturation_prof","Facture N°",domain=[('state', '=', 'P')], required=True)
    x_exercice_id = fields.Many2one("ref_exercice", string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    dte = fields.Date("Date", default=fields.Date.context_today)
    objet = fields.Text("Objet", readonly=True)
    ht = fields.Integer("Montant Total sans remise", readonly=True)
    remise = fields.Integer("Remise",readonly=True)
    total_ht = fields.Integer("Montant Total HT",readonly=True)
    tva = fields.Integer("TVA (18%)", readonly=True)
    tvaex = fields.Boolean("TVA ?", readonly=True)
    ttc = fields.Integer("Montant Total TTC", readonly=True)
    reste = fields.Integer("Reste à payer", readonly=True)
    etat = fields.Selection([('N','Non Payé'),('V','Validé'),('PP','Payé Partiellement'),('P','Payé'),('A','Annulée')],string="Etat", default='N')
    facture_ids = fields.One2many("compta_facturation_ligne","facture_id_def", readonly=True)
    signataire_dcm = fields.Many2one("budg_signataire", default=lambda self: self.env['budg_signataire'].search([('code','=', 'DCM')]))
    signataire_dg = fields.Many2one("budg_signataire", default=lambda self: self.env['budg_signataire'].search([('code','=', 'DG')]))
    text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
    qr_code = fields.Binary("QR Code", attachment=True, store=True)
    structure_id = fields.Many2one('compta_structure', 'Structure', readonly=True)

    current_users = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)

    @api.onchange('current_users')
    def User(self):
        if self.current_users:
            self.x_exercice_id = self.current_users.x_exercice_id


    """"
    @api.constrains('x_exercice_id')
    def _ControleExercice(self):
        no_ex = int(self.x_exercice_id)
        v_ex = int(self.x_exercice_id.no_ex)
        for record in self:
            record.env.cr.execute("select count(id) from ref_exercice where etat = 1 and id = %d" % (no_ex))
            res = self.env.cr.fetchone()
            val = res and res[0] or 0
            if val == 0:
                raise ValidationError(_("Exercice" + " " + str(v_ex) + " " + "est clôs. Traitement impossible"))"""
    
    """
    @api.depends('num_facture','company_id')
    def generate_qr_code(self):
        
        code = str(self.company_id.code_struct)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
            )
        qr.add_data(code+"-"+ self.num_facture)
        qr.make(fit=True)
        img = qr.make_image(fill_color = "black", back_color = "white")
        temp = BytesIO()
        img.save(temp,format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_code = qr_image
    """


    @api.depends('ttc')
    def amount_to_words(self):
        self.text_amount = num2words(self.ttc, lang='fr')
    
    
    @api.onchange('num_facture_prof')
    def lignefacture(self):
        for x in self:
            if x.num_facture_prof:
                x.objet = x.num_facture_prof.objet
                x.telephone = x.num_facture_prof.telephone
                x.structure_id = x.num_facture_prof.structure_id
                x.client_id = x.num_facture_prof.client_id
                x.ht = x.num_facture_prof.ht
                x.tva = x.num_facture_prof.tva
                x.remise = x.num_facture_prof.remise
                x.total_ht = x.num_facture_prof.total_ht
                x.tvaex = x.num_facture_prof.tvaex
                x.ttc = x.num_facture_prof.ttc
                x.reste = x.ttc
                x.facture_ids = x.num_facture_prof.facture_ids
    
    def valider_facture(self):
        v_id = int(self.num_facture_prof)
        for x in self:
            x.env.cr.execute("""update compta_facturation_prof set state = 'T' where id = %d""" %(v_id))
            x.write({'etat': 'V'})
            self.confirmer()
    
    @api.multi
    def confirmer(self):

        v_ex = int(self.current_users.x_exercice_id)
        self.x_exercice_id = v_ex
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select nodef from compteur_def where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct) )
        eng = self.env.cr.fetchone()
        no_eng = eng and eng[0] or 0
        c1 = int(no_eng) + 1
        c = str(no_eng)
        if c == "0":
            ok = str(c1).zfill(5)
            self.num_facture = ok
            vals = c1
            self.env.cr.execute("""INSERT INTO compteur_def(x_exercice_id,company_id,nodef)  VALUES(%d ,%d, %d)""" %(val_ex, val_struct,vals))    
        else:
            c1 = int(no_eng) + 1
            c = str(no_eng)
            ok = str(c1).zfill(5)
            self.num_facture = ok
            vals = c1
            self.env.cr.execute("UPDATE compteur_def SET nodef = %d WHERE x_exercice_id = %d and company_id = %d" %(vals, val_ex, val_struct))




class FacturationPaie(models.Model):
    _name = "compta_facturation_paie"
    _rec_name = "num_facture"
    
    client_id = fields.Many2one("ref_contribuable", "DOIT :", readonly=True)
    telephone = fields.Char("Téléphone", readonly=True)
    num_facture = fields.Char("Facture N°", readonly=True)
    num_facture_def = fields.Many2one("compta_facturation","Facture N°",domain=['|',('etat', '=', 'V'),('etat', '=', 'PP')], required=True)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    dte = fields.Date("Date", default=fields.Date.context_today, readonly=True)
    objet = fields.Text("Objet", readonly=True)
    ht = fields.Integer("Total HT", readonly=True)
    tva = fields.Integer("TVA (18%)", readonly=True)
    tvaex = fields.Boolean("TVA ?", readonly=True)
    ttc = fields.Integer("Total à payer", readonly=True)
    etat = fields.Selection([('N','Non validé'),('V','Validé'),('T','Traité')],string="Etat", default='N')
    facture_ids = fields.One2many("compta_facturation_ligne","facture_id_paie", readonly=False)
    paiement_total = fields.Boolean("Paiement total ou partiel ?")
    mt_souhaite = fields.Integer("Montant à payer souhaité", default= 0)
    total = fields.Integer("Total", default= 0)
    signataire_dcm = fields.Many2one("budg_signataire", default=lambda self: self.env['budg_signataire'].search([('code','=', 'DCM')]))
    


    
    @api.onchange('num_facture_def')
    def lignefacture(self):
        for x in self:
            if x.num_facture_def:
                x.objet = x.num_facture_def.objet
                x.ht = x.num_facture_def.ht
                x.client_id = x.num_facture_def.client_id
                x.telephone = x.num_facture_def.telephone
                x.tva = x.num_facture_def.tva
                x.tvaex = x.num_facture_def.tvaex
                x.ttc = x.num_facture_def.ttc
                x.facture_ids = x.num_facture_def.facture_ids
                
                
    def valider_facture(self):
        v_id = int(self.id)
        val_struc = int(self.company_id)
        for x in self:
            mt = x.mt_souhaite
            """x.env.cr.execute("select sum(l.prix) from compta_facturation_ligne l, compta_facturation_paie p where p.id = l.facture_id_paie and l.facture_id_paie = %d"% (v_id))
            res = x.env.cr.fetchone()
            x.total = res and res[0] or 0"""
            
            if x.paiement_total == False:
                x.env.cr.execute("update compta_facturation set reste = reste - %s, etat = 'PP' where id = %s",(mt, v_id))
                x.env.cr.execute("update compta_facturation set reste = reste - %s, etat = 'P' where id = %s",(mt, v_id))
            """
            if x.paiement_total == False and x.tva == True:
                mt = x.mt_souhaite
                if x.mt_souhaite == 0:
                    raise ValidationError(_("Veuillez renseignez le montant à payer souhaité !"))
                else:
                    x.env.cr.execute("select sum(l.prix) from compta_facturation_ligne l, compta_facturation_paie p where p.id = l.facture_id_paie and l.facture_id_paie = %d"% (v_id))
                    res = x.env.cr.fetchone()
                    self.total = res and res[0] or 0
                    print("resu", resu)

                    montant = mt / resu
                    print("montant", montant)
                    
                    x.env.cr.execute("select taux, compte_id FROM compta_param_tva WHERE company_id = %d" %(val_struc))

                    res = self.env.cr.dictfetchall()
                    tau = res and res[0]["taux"]
                    print("taux", tau)
                    id_imput_tva = res and res[0]["compte_id"]
                    print("id_tva",id_imput_tva)

                    x.env.cr.execute("update compta_facturation_ligne set tva = %s * 0.18, prix = %s - tva, prix_total = prix + tva, id_imput_tva = %s where facture_id_paie = %s",(montant, montant, id_imput_tva, v_id))

                    x.env.cr.execute("update compta_facturation set reste = reste - %s, etat = 'PP' where id = %s",(mt, v_id))

            elif x.paiement_total == False and x.tva == False:
                mt = x.mt_souhaite
                if x.mt_souhaite == 0:
                    raise ValidationError(_("Veuillez renseignez le montant à payer souhaité !"))
                else:
                    x.env.cr.execute("select count(l.id) from compta_facturation_ligne l, compta_facturation_paie p where p.id = l.facture_id_paie and l.facture_id_paie = %d" % (v_id))
                    res = x.env.cr.fetchone()
                    resu = res and res[0] or 0

                    montant = mt / resu

                    x.env.cr.execute("update compta_facturation_ligne set tva = 0 prix = %s , prix_total = prix  where facture_id_paie = %s",(montant, v_id))

                    x.env.cr.execute("update compta_facturation set reste = reste - %s, etat = 'PP' where id = %s",(mt, v_id))
            else:
                mt = x.ttc

                x.env.cr.execute("update compta_facturation_ligne set prix = %s where facture_id_paie = %s",(mt, v_id))

                x.env.cr.execute("update compta_facturation set reste = reste - %s, etat = 'P' where id = %s",(mt, v_id))
            """
            x.confirmer()
            
            x.write({'etat': 'V'})


            
    
    @api.multi
    def confirmer(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        
        self.env.cr.execute("select nopaie from compteur_paie where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct) )
        eng = self.env.cr.fetchone()
        no_eng = eng and eng[0] or 0
        c1 = int(no_eng) + 1
        c = str(no_eng)
        if c == "0":
            ok =str(c1).zfill(8)
            self.num_facture = ok
            vals = c1
            self.env.cr.execute("""INSERT INTO compteur_paie(x_exercice_id,company_id,nopaie)  VALUES(%d ,%d, %d)""" %(val_ex, val_struct,vals))    
        else:
            c1 = int(no_eng) + 1
            c = str(no_eng)
            ok = str(c1).zfill(8)
            self.num_facture = ok
            vals = c1
            self.env.cr.execute("UPDATE compteur_paie SET nopaie = %d WHERE x_exercice_id = %d and company_id = %d" %(vals, val_ex, val_struct))


class CompteurPro(models.Model):
    
    _name = "compteur_pro"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    nopro = fields.Integer(default = 0)

class CompteurPaie(models.Model):
    
    _name = "compteur_paie"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    nopaie = fields.Integer(default = 0)

class CompteurDef(models.Model):
    
    _name = "compteur_def"
    
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    nodef = fields.Integer(default = 0)


class ComptaStructure(models.Model):
    _name = "compta_structure"

    name = fields.Char('Structure', required=True)
    description = fields.Text()
    active = fields.Boolean('Actif', default=True)
             
                


  
    



    