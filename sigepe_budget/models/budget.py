from odoo import api, models, fields, _, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date
from email.policy import default
from num2words import num2words
from collections import OrderedDict


#Definitions des différentes classes

class Budg_TypeAccompte(models.Model):

	_name = "budg_typeaccompte"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_accompte = fields.Char(string = "Code", size = 2, required=True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)

	
class Budg_TypeBudget(models.Model):

	_name = "budg_typebudget"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_budget = fields.Char(string = "Code", size = 2, required=True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)


class Budg_TypeBordTrans(models.Model):

	_name = "budg_typebordtrans"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	code = fields.Char(string = "Code", size = 2)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	type_depart = fields.Selection([
        ('ORD', 'ORD'),
        ('CF/CG', 'CF/CG'),
        ('AC', 'AC'),
        ], string ="Départ")
	type_dest = fields.Selection([
        ('ORD', 'ORD'),
        ('CF', 'CF'),
        ('AC', 'AC'),
        ], string ="Destinataire")
	active = fields.Boolean('Actif',default=True)



class Budg_TypeControle(models.Model):

	_name = "budg_typecontrole"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_controle = fields.Char(string = "Code", default=lambda self: self.env['ir.sequence'].next_by_code('cd_type_controle'), readonly = True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)


class Budg_TypeContribuable(models.Model):

	_name = "budg_typecontribuable"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_contribuable = fields.Char(string = "Code", default=lambda self: self.env['ir.sequence'].next_by_code('cd_type_contribuable'), readonly = True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)



class Budg_TypeDepense(models.Model):

	_name = "budg_typedepense"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_depense = fields.Char(string = "Code", default=lambda self: self.env['ir.sequence'].next_by_code('cd_type_contribuable'), readonly = True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)
	_sql_constraints = [
        ('cd_type_depense', 'unique (cd_type_depense)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


class Budg_TypeDossierBudg(models.Model):

	_name = "budg_typedossierbudg"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	code = fields.Char(string = "Code", readonly = False)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)

	
	
class Budg_Typeprocedure(models.Model):
	
	_name = 'budg_typeprocedure'
	_rec_name = 'lb_long'
	
	sequence = fields.Integer(default=10)
	type_procedure = fields.Char(string = "Code", default=lambda self: self.env['ir.sequence'].next_by_code('type_procedure'), readonly = True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)



class Budg_TypeEngagement(models.Model):

	_name = "budg_typeengagement"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	type_procedure_id = fields.Many2one('budg_typeprocedure',string = "Type procédure")
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)



class Budg_TypeOrdrePaiement(models.Model):

	_name = "budg_typeordrepaiement"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_ordre_paiement = fields.Char(string = "Code", default=lambda self: self.env['ir.sequence'].next_by_code('cd_type_ordre_paiement'), readonly = True)
	type_procedure = fields.Many2one('budg_typeprocedure',string = "Type procédure")
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)


class Budg_TypePieceBudget(models.Model):

	_name = "budg_typepiecebudget"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_piece_budget = fields.Char(string = "Code",default=lambda self: self.env['ir.sequence'].next_by_code('cd_type_piece_budget'), readonly = True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)



class budg_PJ(models.Model):
	
	_name = "budg_pj"
	_rec_name="lb_long"
	
	lb_long = fields.Many2one("budg_typepjbudget",string = "Libellé long", size = 100, required=True)
	oblige = fields.Boolean("Obligé ?")
	nombre = fields.Integer("Nbre copies(s)")
	ref = fields.Char("Références")
	montant = fields.Integer("Montant")
	param_article_id = fields.Many2one("budg_param_article")
	recette_id = fields.Many2one("budg_titrerecette")
	liq_id = fields.Many2one('budg_liqord')
	mandat_id = fields.Many2one('budg_mandat')
	

class budg_PJ_REC(models.Model):
	
	_name = "budg_pj_rec"
	_rec_name="lb_long"
	
	lb_long = fields.Many2one("budg_typepjbudget",string = "Libellé long", size = 100, required=True)
	oblige = fields.Boolean("Obligé ?")
	nombre = fields.Integer("Nbre copies(s)")
	ref = fields.Char("Références")
	montant = fields.Integer("Montant")
	nature_rec_id = fields.Many2one("budg_naturerecette")

	

class Budg_NatureRecette(models.Model):

	_name = "budg_naturerecette"
	_rec_name = "cd_paragraphe_id"

	sequence = fields.Integer(default=10)
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre",default=lambda self: self.env['budg_titre'].search([('type_titre','=', 'R')]),readonly=True, required=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", required=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", required=True)
	lb_long = fields.Many2one("ref_article",string = "Nature de la recette", required=False)
	typebenef = fields.Many2one("ref_typecontribuable", "Type de contribuable", required=False)
	cat_benef = fields.Many2one("ref_categoriecontribuable","Catégorie de contribuable", required=False)
	pj_ids = fields.One2many("budg_pj_rec", 'nature_rec_id')
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	
	

class Budg_NatureDepense(models.Model):

	_name = "budg_naturedepense"
	_rec_name = "cat_benef"

	sequence = fields.Integer(default=10)
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre",default=lambda self: self.env['budg_titre'].search([('type_titre','=', 'D')]),readonly=True, required=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", required=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", required=True)
	lb_long = fields.Many2one("ref_article",string = "Nature de la dépense", required=False)
	cd_type_dossier_id = fields.Many2one('budg_typedossierbudg', required=True, string="Etape",default=lambda self: self.env['budg_typedossierbudg'].search([('code','=', 'ENG')]) )
	type_procedure_id = fields.Many2one('budg_typeprocedure', string="Type de procédure", required=True)
	typebenef = fields.Many2one("ref_typebeneficiaire", "Type de bénéficiaire", required=False)
	cat_benef = fields.Many2one("ref_categoriebeneficiaire","Catégorie de beneficiaire", required=True)
	pj_ids = fields.One2many("budg_pj_dep", 'nature_dep_id')
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	
	
	
class budg_PJ_DEP(models.Model):
	
	_name = "budg_pj_dep"
	_rec_name="lb_long"
	
	lb_long = fields.Many2one("budg_typepjbudget",string = "Libellé long", size = 100, required=True)
	oblige = fields.Boolean("Obligatoire")
	nombre = fields.Integer("Nbre copies(s)")
	ref = fields.Char("Références")
	montant = fields.Integer("Montant")
	nature_dep_id = fields.Many2one("budg_naturedepense")




class Budg_PieceJusti(models.Model):
	
	_name = "budg_piecejustificative"
	_rec_name = "cd_piecejust_id"
	
	sequence = fields.Integer(default=10)
	cd_piecejust_id = fields.Many2one('budg_typepjbudget', string="Intitulé")
	reference = fields.Char("Références", size = 35)
	datepj = fields.Date('Date')
	active = fields.Boolean("Obligé ?",default=True)
	montant = fields.Integer('Montant', size= 15)
	nombre = fields.Integer("Nbre copies(s)", size = 2)
	eng_id = fields.Many2one('budg_engagement')
	


class Budg_TypePJBudget(models.Model):

	_name = "budg_typepjbudget"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_pj_budget = fields.Char(string = "Code ", size = 3)
	name = fields.Char(string = "Libellé court", size = 50, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	lb_ref = fields.Char(string="Ref", size=65)
	active = fields.Boolean('Actif',default=True)


class Budg_ModeMarche(models.Model):

	_name = "budg_modemarche"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_mode_mp = fields.Char(string = "Mode marché", default=lambda self: self.env['ir.sequence'].next_by_code('cd_mode_mp'), readonly=True) 
	name = fields.Char(string = "Libellé court", size = 25)
	lb_long = fields.Char(string = "Libellé long", size = 65)
	active = fields.Boolean('Actif',default=True)


class Budg_TypeTitreBudgetaire(models.Model):

	_name = "budg_typetitrebudgetaire"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_titre_budgetaire = fields.Char(string = "Code", size = 2, required=True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)

	_sql_constraints = [
        ('cd_titre_budgetaire', 'unique (cd_titre_budgetaire)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


class Budg_TitreRecette(models.Model):

	_name = "budg_titrerecette"
	_rec_name = "cd_titre_recette"
	_order = "id desc"

	cd_titre_recette = fields.Char(string = "N° titre recette", readonly=True)
	name = fields.Char()
	no_grpadm = fields.Char()
	cd_titre_id = fields.Many2one("budg_titre",default=lambda self: self.env['budg_titre'].search([('type_titre','=', 'R')]), string = "Titre", required=True, readonly=True)
	cd_section_id = fields.Many2one("budg_section", string = "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", required=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", required=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", required=True)
	titre_id = fields.Char()
	section_id = fields.Char()
	chapitre_id = fields.Char()
	article_id = fields.Char()
	paragraphe_id = fields.Char()
	rubrique_id = fields.Char()
	no_grpadm_pere = fields.Char(size = 4)
	no_rec_pere = fields.Char(size = 4)
	no_bord_prec = fields.Integer(size = 5)
	no_brj_prec = fields.Integer(size =5)
	no_bailleur = fields.Many2one("ref_bailleur",string="Nom")
	contribuable_id = fields.Many2one("ref_contribuable", string = "Nom du débiteur", size = 65, required=True)
	type_titre = fields.Selection([
        ('N', 'Avant recouvrement'),
        ('R', 'Régularisation'),
        ], 'Type titre recette',  track_visibility='always', required=True)
	categorie_contribuable = fields.Many2one("ref_categoriecontribuable", string = "Cat cont", required=False)
	nature_rec = fields.Many2one("ref_article", string="Nature de recette", required=False)
	cd_type_contribuable = fields.Many2one("ref_typecontribuable", string="Type contrib/client", required=True)
	lb_objet = fields.Text(string = "Objet", size = 250, required=True)
	mnt_init_rec = fields.Float(string="Montant initial recette")
	mnt_rec = fields.Float(string="Montant titre recette", required=True)
	nb_pjust = fields.Integer(size = 2)
	piecejust_ids = fields.One2many("budg_piece_recette",'recette_id')
	mnt_lbudg_ap = fields.Float(string="Montant lbudg ap")
	mnt_period_ap = fields.Float()
	mnt_recouvre = fields.Float("Reste à recouvrer",digits = (20,0), readonly=True)
	mnt_vbr = fields.Float()
	mnt_ecr = fields.Float()
	mnt_annule = fields.Float()
	imput = fields.Integer()
	no_imputation = fields.Char()
	no_imput = fields.Integer()
	tx_obj1 = fields.Char(size=15)
	type_budget_id = fields.Many2one("budg_typebudget")
	dt_rec = fields.Date(default=fields.Date.context_today,string="Date", readonly=True)
	dt_app = fields.Date()
	dt_valid = fields.Date()
	dt_visa_ac = fields.Date()
	dt_visa_ord = fields.Date()
	no_cpt_deb = fields.Char(size=3)
	no_scpt_deb = fields.Char(size=11)
	no_cpt_cred = fields.Char(size=3)
	no_scpt_cred = fields.Char(size=11)
	x_exercice_id_lecr = fields.Integer(size=4)
	no_lecr_deb = fields.Integer()
	no_lecr_pc_deb = fields.Integer()
	no_lecr_pc_cred = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	cd_mode_mp_id = fields.Many2one("ref_modereglement", string = "Mode de recouvrement")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	et_doss = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Confirmé'),
        ('V', 'Approuvé'),
		('A', 'Annulé'),
		('W', 'Visé CF/CG'),
		('R', 'Rejeté CF/CG'),
		('I', 'Visa AC'),
		('J', 'Rejét AC'),
		('E', 'Pris en charge'),
		('F', 'Recouvré'),
        ], 'Etat', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
	

	_sql_constraints = [
        ('cd_titre_recette', 'unique (cd_titre_recette)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
	
	@api.depends('mnt_rec')
	def amount_to_words(self):
		self.text_amount = num2words(self.mnt_rec, lang='fr')
	
		
	@api.onchange('cd_type_contribuable')
	def onchangeTypeCont(self):
		if self.cd_type_contribuable:
			self.categorie_contribuable = self.cd_type_contribuable.cate_id
			self.imput = self.cd_type_contribuable.cpte_client.souscpte.id
	
	@api.onchange('cd_rubrique_id')
	def onchangeType(self):
		if self.cd_rubrique_id:
			self.no_imputation = str(self.cd_rubrique_id.rubrique) + " " + str(self.cd_rubrique_id.no_imputation.souscpte.lb_long)
			self.no_imput = self.cd_rubrique_id.no_imputation.souscpte.id
			self.rubrique_id = self.cd_rubrique_id.rubrique
	
	@api.onchange('cd_paragraphe_id')
	def onchangePar(self):
		if self.cd_paragraphe_id:
			
				self.paragraphe_id = self.cd_paragraphe_id.paragraphe.cd_paragraphe
	
	@api.onchange('cd_titre_id')
	def onchangeTit(self):
		if self.cd_titre_id:
			
				self.titre_id = self.cd_titre_id.titre.cd_titre
				
	@api.onchange('cd_section_id')
	def onchangeSec(self):
		if self.cd_section_id:
			
				self.section_id = self.cd_section_id.section.cd_section
	
				
	@api.onchange('cd_article_id')
	def onchangeArt(self):
		if self.cd_article_id:
			
				self.article_id = self.cd_article_id.article.cd_article
	
	@api.onchange('cd_chapitre_id')
	def onchangeCha(self):
		if self.cd_chapitre_id:
			
				self.chapitre_id = self.cd_chapitre_id.chapitre.cd_chapitre
	
	
	@api.multi
	def action_rec_draft(self):
		self.write({'et_doss': 'draft'})
		
		
	@api.onchange('cd_rubrique_id', 'cd_paragraphe_id')
	def cred_dipso(self):
		
		val_ex = int(self.x_exercice_id.id)
		val_struct = int(self.company_id.id)
		val_para = int(self.cd_paragraphe_id)
		val_rubrique = int(self.cd_rubrique_id)
		
		result = self.env['budg_ligne_exe_rec'].search([('cd_paragraphe_id','=',val_para),('cd_rubrique_id','=',val_rubrique),('company_id','=',val_struct),('x_exercice_id','=',val_ex)])
		self.mnt_recouvre = result.reste_emettre
	

	@api.multi
	def action_rec_confirmer(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
	
		self.env.cr.execute("select notitre from budg_compteur_titrerec where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
		notitre = self.env.cr.fetchone()
		cd_titre_recette = notitre and notitre[0] or 0
		c1 = int(cd_titre_recette) + 1
		c = str(cd_titre_recette)
		if c == "0":
			ok = str(c1).zfill(4)
			self.cd_titre_recette = ok
			vals = c1			
			self.env.cr.execute("INSERT INTO budg_compteur_titrerec(x_exercice_id,company_id,notitre)  VALUES(%d, %d, %d)" %(val_ex,val_struct,vals))
		else:
			c1 = int(cd_titre_recette) + 1
			c = str(cd_titre_recette)
			ok = str(c1).zfill(4)
			self.cd_titre_recette = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_titrerec SET notitre = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))
			
		self.write({'et_doss': 'N'})
		
		
			
	@api.multi
	def action_rec_approuver(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_rub = int(self.cd_rubrique_id)
		val_titre = int(self.cd_titre_id)
		val_sec = int(self.cd_section_id)
		val_par = int(self.cd_paragraphe_id)
		val_chap = int(self.cd_chapitre_id)
		val_rub = int(self.cd_rubrique_id)
		val_art = int(self.cd_article_id)
		v_id = int(self.id)
		
		
		self.env.cr.execute("""UPDATE budg_ligne_exe_rec SET mnt_rec = (select sum(T.mnt_rec) 
		FROM budg_ligne_exe_rec BT, budg_titrerecette T WHERE T.id = %d AND BT.cd_titre_id = %d and 
		BT.cd_section_id = %d and BT.cd_chapitre_id = %d and BT.cd_art_id = %d and BT.cd_paragraphe_id = %d and 
		BT.cd_rubrique_id = %d and BT.x_exercice_id = %d and BT.company_id = %d group by T.mnt_rec) WHERE cd_titre_id = %d and 
		cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d and 
		cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d
		""" %(v_id, val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct,val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct))

	
		self.env.cr.execute("""UPDATE budg_ligne_exe_rec SET reste_emettre = (select (BT.mnt_corrige - sum(T.mnt_rec)) 
		FROM budg_ligne_exe_rec BT, budg_titrerecette T WHERE T.id = %d AND BT.cd_titre_id = %d and 
		BT.cd_section_id = %d and BT.cd_chapitre_id = %d and BT.cd_art_id = %d and BT.cd_paragraphe_id = %d and 
		BT.cd_rubrique_id = %d and BT.x_exercice_id = %d and BT.company_id = %d group by BT.mnt_corrige) WHERE cd_titre_id = %d and 
		cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d and 
		cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d
		""" %(v_id,val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct,val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct))


	
		self.env.cr.execute("""UPDATE budg_ligne_exe_rec SET taux = (select ((sum(T.mnt_rec) * 100) / BR.mnt_corrige)  
		FROM budg_ligne_exe_rec BR, budg_titrerecette T WHERE T.id = %d AND BR.cd_titre_id = %d and 
		BR.cd_section_id = %d and BR.cd_chapitre_id = %d and BR.cd_art_id = %d and BR.cd_paragraphe_id = %d and 
		BR.cd_rubrique_id = %d and BR.x_exercice_id = %d and BR.company_id = %d group by BR.mnt_corrige) WHERE cd_titre_id = %d and 
		cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d and 
		cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d
		""" %(v_id,val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct,val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct))
	

		self.write({'et_doss': 'V'})
		self.dt_app = date.today()
		
	@api.multi
	def action_rec_annuler(self):
		self.write({'et_doss': 'A'})
		
	@api.multi
	def action_rec_viser(self):
		self.write({'et_doss': 'W'})
		self.dt_visa_ord = date.today()
		
	@api.multi
	def action_rec_rejeter(self):
		self.write({'et_doss': 'R'})
		
	@api.multi
	def action_rec_viser_ac(self):
		self.write({'et_doss': 'I'})
		
	@api.multi
	def action_rec_rejeter_ac(self):
		self.write({'et_doss': 'J'})
		
	@api.multi
	def action_rec_pc(self):
		self.write({'et_doss': 'E'})
		
	def afficher_piece(self):
        
		val_ex = int(self.x_exercice_id)
		categorie = int(self.categorie_contribuable)
		titre = int(self.cd_titre_id)
		section = int(self.cd_section_id)
		chapitre = int(self.cd_chapitre_id)
		article = int(self.cd_article_id)
		paragraphe = int(self.cd_paragraphe_id)

		
		for vals in self:
		    vals.env.cr.execute("""select b.lb_long as lib, b.oblige as obl, b.nombre as nbr from budg_pj_rec b, budg_naturerecette n where n.cat_benef = %d
			and n.cd_titre_id = %d and n.cd_section_id = %d and n.cd_chapitre_id = %d and n.cd_article_id = %d and n.cd_paragraphe_id = %d 
			and n.x_exercice_id = %d and n.id = b.nature_rec_id""" %(categorie,titre, section, chapitre, article, paragraphe, val_ex))
		    rows = vals.env.cr.dictfetchall()
		    result = []
		    
		    vals.piecejust_ids.unlink()
		    for line in rows:
		        result.append((0,0, {'lb_long' : line['lib'], 'oblige': line['obl'], 'nombre': line['nbr']}))
		    self.piecejust_ids = result
	
		
class Budg_Compteur_titrerec(models.Model):
	
	_name = "budg_compteur_titrerec"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	notitre = fields.Integer(default = 0)


class Budg_bord_titre(models.Model):
	
	_name = "budg_bord_titre_recette"
	_rec_name = "no_bord_rec"
	
	name = fields.Char()
	no_bord_rec = fields.Char("N° Bord", readonly=True)
	cd_acteur = fields.Char(string ="Acteur", readonly=True)
	date_emis = fields.Date("Date bordereau", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date()
	num_accuse = fields.Char()
	totaux = fields.Float()
	type_bord_trsm = fields.Char("Type de bordereau", readonly=True)
	cd_acteur_accuse = fields.Char(string ="Acteur accusé")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	recette_ids = fields.Many2many("budg_titrerecette", "budg_detail_bord_recette", string="Liste des titres de recettes", ondelete="restrict")
	et_doss = fields.Selection([
        ('N', 'Nouveau'),
        ('EB', 'Mise en bordereau'),
		('RB', 'Réception bord. DAF/DFC'),
		('EC', 'Envoi bord. CF/CG'),
		('RC', 'Réception bord. CF/CG'),
		('V', 'Envoi pr PC'),
		('PC', 'Réception pr PC'),
        ], 'Etat', default='N', required=True)
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)


	@api.multi
	def action_reception_bord_daf_cf(self):
		self.write({'et_doss': 'RB'})

	@api.multi
	def action_envoi_bord_cf_daf(self):
		self.write({'et_doss': 'EC'})
		
	@api.multi
	def action_reception_bord_cf_daf(self):
		self.write({'et_doss': 'RC'})
	
	@api.multi
	def action_envoyer_bord_pc(self):
		self.write({'et_doss': 'V'})
	
	@api.multi
	def action_reception_bord_pc(self):
		self.write({'et_doss': 'PC'})
		
	@api.depends('totaux')
	def amount_to_words(self):
		self.text_amount = num2words(self.totaux, lang='fr')
		
	
	@api.multi
	def action_generer_bord_titre(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_id = int(self.id)
		
			
		self.env.cr.execute("select bordtitre from budg_compteur_bord_titre where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
		bordtitre = self.env.cr.fetchone()
		no_bord_titre = bordtitre and bordtitre[0] or 0
		c1 = int(no_bord_titre) + 1
		c = str(no_bord_titre)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_bord_rec = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_bord_titre(x_exercice_id,company_id,bordtitre)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))	
		else:
			c1 = int(no_bord_titre) + 1
			c = str(no_bord_titre)
			ok = str(c1).zfill(4)
			self.no_bord_rec = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_bord_titre SET bordtitre = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))
	
		self.write({'et_doss': 'EB'})
		
		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '13' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '13' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '13' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0
		
		
		self.env.cr.execute(""" SELECT sum(mnt_rec) FROM budg_titrerecette bt , budg_bord_titre_recette b, budg_detail_bord_recette br
		WHERE b.x_exercice_id = %d AND b.company_id = %d AND br.budg_bord_titre_recette_id = %d 
		AND bt.id = br.budg_titrerecette_id AND br.budg_bord_titre_recette_id = b.id""" %(val_ex,val_struct, val_id))
		res = self.env.cr.fetchone()
		self.totaux = res and res[0] or 0
		print('montant',self.totaux)

	
"""	
class Budg_TypeBeneficiaire(models.Model):

	_name = "budg_typebeneficiaire"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_beneficiaire = fields.Char(string = "Code", size = 2, required=True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)

	_sql_constraints = [
        ('cd_type_beneficiaire', 'unique (cd_type_beneficiaire)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
"""

class Budg_TypeFinancement(models.Model):

	_name = "budg_typefinancement"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_financement = fields.Char(string = "Code", size = 2, required=True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)

	_sql_constraints = [
        ('cd_type_financement', 'unique (cd_type_financement)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


class Budg_TypeRecette(models.Model):

	_name = "budg_typerecette"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_recette = fields.Char(string = "Code", size = 2)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)

	_sql_constraints = [
        ('cd_type_recette', 'unique (cd_type_recette)', "Ce code existe déjà. Veuillez changer de code !"),
    ]



class Budg_TypeFournisseur(models.Model):

	_name = "budg_typefournisseur"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_type_fournisseur = fields.Char(string = "Code", size = 2, required=True)
	name = fields.Char(string = "Libellé court", size = 25, required=True)
	lb_long = fields.Char(string = "Libellé long", size = 100, required=True)
	active = fields.Boolean('Actif',default=True)

	_sql_constraints = [
        ('cd_type_fournisseur', 'unique (cd_type_fournisseur)', "Ce code existe déjà. Veuillez changer de code !"),
    ]

"""
class BudgBeneficiaire(models.Model):

	_name = "budg_beneficiaire"
	_rec_name = "nm"
	
	name = fields.Char(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('name'), readonly = True)
	no_beneficiaire = fields.Char(string="Raison sociale", size=65)
	type_beneficiaire_id = fields.Many2one("budg_typebeneficiaire",string="Type de bénéficiaire")
	nm = fields.Char(string="Nom et Prénom", size=20)
	pn = fields.Char(string="Prénom", size=40)
	no_ifu = fields.Char(string="N° IFU", size=20)
	cd_mat = fields.Char(string="Matricule", size=20)
	no_eng = fields.Integer(string="No_Eng")
	ex_last = fields.Integer(string="Ex_last")
	ap_rue = fields.Char(string="Rue", size=35)
	ap_bp = fields.Char(string="Boite postale", size=8)
	ap_cd_post = fields.Char(string="Code postal", size=6)
	ap_ville = fields.Char(string="Ville", size=30)
	ap_pays = fields.Many2one("ref_pays",string="Pays")
	tel = fields.Char(string="Téléphone", size=30)
	nm_officiel = fields.Char(string="Titre officiel", size=50)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	mod_reg_id = fields.Many2one("ref_modereglement", string="Mode") 
	bank_id = fields.Many2one("res.bank", string = "Banque")
	active = fields.Boolean('Actif',default=True)
	fg_bloc = fields.Char()
	cpte_client = fields.Many2one("ref_souscompte", string = "Compte client")
	cpte_fournisseur = fields.Many2one("ref_souscompte", string = "Compte fournisseur")
	agence_bank_id = fields.Char(string = "N° Agence")
	acc_number = fields.Char(string = "N° compte")
	cat_fournisseur = fields.Selection([
		('S', 'Société'),
		('P', 'Particulier')], 'Catégorie ')

	_sql_constraints = [
        ('no_beneficiaire', 'unique (no_beneficiaire)', "Ce code existe déjà. Veuillez changer de code !"),
    ]
"""

class ResPartner(models.Model):
	
	_inherit = "res.partner"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class BudgBailleur(models.Model):

	_name = "budg_bailleur"
	_rec_name = "nm_bail"
	
	name = fields.Char()
	cd_bail = fields.Char(string="Code Bailleur", default=lambda self: self.env['ir.sequence'].next_by_code('cd_bail'), readonly = True)
	type_bailleur = fields.Selection([
        ('P', 'Particulier'),
        ('S', 'Société/Institution'),
        ], string ="Type de bailleur", default='P')
	nm_bail = fields.Char(string="Nom Bailleur", size=60)
	lb_sigle = fields.Char(string="Libellé sigle", size=60)
	na_bail = fields.Char(string="na_bail", size=1)
	cd_categ = fields.Char(string="Catégorie", size=4)
	ap_rue = fields.Char(string="Rue", size=35)
	ap_bp = fields.Char(string="Boite Postale", size=8)
	ap_cd_post = fields.Char(string="Code Postale", size=6)
	ap_ville = fields.Char(string="Ville", size=30)
	ap_pays = fields.Many2one("ref_pays",string="Pays", size=3)
	as_rue = fields.Char(string="Rue 2nd", size=35)
	as_bp = fields.Char(string="Boite Postale 2nd", size=8)
	as_cd_post = fields.Char(string="Code Postale 2nd", size=6)
	as_ville = fields.Char(string="Ville 2nd", size=30)
	as_pays = fields.Many2one("ref_pays",string="Pays 2nd", size=8)
	tel = fields.Char(string="Téléphone", size=30)
	mail = fields.Char(string="Mail", size=50)
	site = fields.Char(string="Site WEB", size=50)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bank_id = fields.Many2one("res.bank", string = "Banque")
	acc_bank_id = fields.Char(string = "N° Compte", size=30)
	active = fields.Boolean('Actif',default=True)

	_sql_constraints = [
        ('cd_bail', 'unique (cd_bail)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


class BudgFournisseur(models.Model):

	_name = "budg_fournisseur"
	_rec_name = 'nm_rs'
	
	
	no_four = fields.Char(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('no_four'), readonly = True)
	type_fournisseur_id = fields.Many2one("budg_typebeneficiaire",string="Type de fournisseur")
	nm_rs = fields.Char(string="Raison sociale ou Nom")
	nm_rs2 = fields.Char(string=" ")
	an_agre = fields.Date(string="Année agrément")
	no_agre = fields.Integer(string="N° Agrément")
	no_ifu = fields.Char(string="N° IFU", size=11)
	cd_citib = fields.Char(string="Cd_CITIB")
	activite = fields.Char(string="Activité", size  = 50)
	ap_rue = fields.Char(string="Rue")
	ap_bp = fields.Char(string="Boite Postale")
	ap_cd_post = fields.Char(string="Code Postale")
	ap_region = fields.Many2one("ref_region",string="Région")
	ap_ville = fields.Char(string="Ville")
	ap_province = fields.Many2one("ref_province",string="Province")
	ap_pays = fields.Many2one("ref_pays",string="Pays")
	rf_txt_agre = fields.Char(string="Texte n°")
	dt_txt_agre = fields.Date(string="Du")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bank_id = fields.Many2one("res.bank", string = "Banque")
	fg_eng = fields.Char()
	active = fields.Boolean('Actif',default=True)
	agence_bank_id = fields.Char(string = "N° Agence")
	acc_number = fields.Char(string = "N° compte")
	tel = fields.Char(string="Téléphone")
	mail = fields.Char(string="Mail")

	_sql_constraints = [
        ('no_four', 'unique (no_four)', "Ce code existe déjà. Veuillez changer de code !"),
    ]

class BudgContribuable(models.Model):

	_name = "budg_contribuable"
	_rec_name = 'nm_rs'
	
	
	no_contrib = fields.Char(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('no_contrib'), readonly = True)
	type_contribuable_id = fields.Many2one("budg_typecontribuable",string="Type de contribuable")
	nm_rs = fields.Char(string="Raison sociale ou Nom")
	nm_rs2 = fields.Char(string=" ")
	an_agre = fields.Date(string="Année agrément")
	no_agre = fields.Integer(string="N° Agrément")
	no_ifu = fields.Char(string="N° IFU", size=11)
	cd_citib = fields.Char(string="Cd_CITIB")
	activite = fields.Char(string="Activité", size  = 50)
	ap_rue = fields.Char(string="Rue")
	ap_bp = fields.Char(string="Boite Postale")
	ap_cd_post = fields.Char(string="Code Postale")
	ap_region = fields.Many2one("ref_region",string="Région")
	ap_ville = fields.Char(string="Ville")
	ap_province = fields.Many2one("ref_province",string="Province")
	ap_pays = fields.Many2one("ref_pays",string="Pays")
	rf_txt_agre = fields.Char(string="Texte n°")
	dt_txt_agre = fields.Date(string="Du")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bank_id = fields.Many2one("res.partner.bank", string = "Banque")
	fg_eng = fields.Char()
	active = fields.Boolean('Actif',default=True)
	agence_bank_id = fields.Char(string = "N° Agence")
	acc_number = fields.Char(string = "N° compte")
	tel = fields.Char(string="Téléphone")
	mail = fields.Char(string="Mail")

	_sql_constraints = [
        ('no_contrib', 'unique (no_contrib)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


# Définitions des classes du menu paramètre

class Budg_Certification(models.Model):

	_name = "budg_certification"
	_rec_name = "lb_long"

	sequence = fields.Integer(default=10)
	cd_certification = fields.Char(string = "Code", size = 2)
	name = fields.Char(string = "Libellé court", size = 25)
	lb_long = fields.Char(string = "Libellé long", size = 65, required=True)
	active = fields.Boolean('Actif',default=True)

	_sql_constraints = [
        ('cd_certification', 'unique (cd_certification)', "Ce code existe déjà. Veuillez changer de code !"),
    ]


class BudgRubrique(models.Model):
	@api.depends('rubrique','lb_long')
	def _concatenate_rub(self):
		for test in self:
			test.concate_rubrique = str(test.rubrique)+ " " +str(test.lb_long)
    
	
	_name = "budg_rubrique"
	_rec_name = "concate_rubrique"

	sequence = fields.Integer(default=10)
	
	concate_rubrique = fields.Char(compute='_concatenate_rub')
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section", string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string="Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)		
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string ="Paragraphe", required=True)
	rubrique_id = fields.Many2one("ref_rubrique",string="Rubrique")
	rubrique = fields.Char(string="Code Rubrique", required=True)
	lb_court = fields.Char("Libellé court", size = 75, required=False)
	lb_long = fields.Char("Libellé long", size = 200, readonly=True)	
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	active = fields.Boolean('Terminal',default=True)
	no_imputation = fields.Many2one("compta_plan_line", string = "Imputation Cptble", required=True)
   
	@api.onchange('cd_paragraphe_id')
	def Rub(self):

		for x in self:
			self.cd_titre_id = self.cd_paragraphe_id.cd_titre_id
			self.cd_section_id = self.cd_paragraphe_id.cd_section_id
			self.cd_chapitre_id = self.cd_paragraphe_id.cd_chapitre_id
			self.cd_article_id = self.cd_paragraphe_id.cd_article_id


	@api.onchange('no_imputation')
	def libelle(self):
		if self.no_imputation:
			self.lb_long = self.no_imputation.libelle


# Définitions des classes du menu marché & contrat

class BudgAppelOffre(models.Model):
	
	_name = "budg_appeloffre"
	_rec_name = "name"

	
	name = fields.Integer(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('name'), required=True)
	ref_ao = fields.Char(string="Référence A.O", size = 25, required=True)	
	cd_titre_id = fields.Many2one("budg_titre",string="Titre",default=lambda self: self.env['budg_titre'].search([('titre', '=', 2)]))
	cd_section_id = fields.Many2one("budg_section",string="Section")
	cd_nature_depense_id = fields.Many2one("budg_naturedepense", string="Nature",required=True)
	cd_mode_mp_id = fields.Many2one("budg_modemarche", string="Mode")
	cd_bailleur_id = fields.Many2one("budg_bailleur", string="Financement")
	objet_ao = fields.Text(string="Objet", size = 300)
	prix_dossier = fields.Integer(string="Prix du dossier",required=True)
	dt_publication = fields.Date(string="Date de publication")
	dt_depouillement = fields.Date(string="Date de dépouillement")
	dt_resultat = fields.Date(string="Date probable des résultats")
	typ_dest = fields.Char(string="Type destinataire")
	id_dest = fields.Char(string="Identifiant destinataire")
	dt_delai = fields.Date(string="Delai d'exécution")
	nb_j_delai = fields.Integer(string="Nombre de jour", size = 2)
	nb_s_delai = fields.Integer(string="Nombre de semaine", size = 2)
	nb_m_delai = fields.Integer(string="Nombre de mois", size = 2)
	nb_a_delai = fields.Integer(string="Nombre d'année", size = 2)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

	_sql_constraints = [
        ('name', 'unique (name)', "Ce code existe déjà. Veuillez changer de code !"),
    ]	


class BudgMarche(models.Model):

	_name = "budg_marche"
	_rec_name = "ref_mp"

	name = fields.Char()
	id_mp = fields.Char(string="Identifiant du marché", default=lambda self: self.env['ir.sequence'].next_by_code('id_mp'), readonly = True)
	ref_mp = fields.Char(string="Référence", required=True)
	id_ao = fields.Many2one("budg_appeloffre", string="Identifiant Appel offre", required=True)
	ref_mp = fields.Char(string="Référence du marché", size = 25)
	objet_marche = fields.Text(string = "Objet", size = 300)
	cd_titre_id = fields.Many2one("budg_titre",string="Titre",default=lambda self: self.env['budg_titre'].search([('titre', '=', 2)]))
	cd_section_id = fields.Many2one("budg_section",string="Section")
	cd_fournisseur_id = fields.Many2one("ref_beneficiaire",string="Bénéficiaire")
	mnt_mp = fields.Integer(string="Montant du marché", size = 15, required=True)
	mnt_eng_cf = fields.Integer(string="Montant engagé CF", size = 15)
	mnt_liq_cf = fields.Integer(string="Montant liquidé CF", size = 15)
	dt_notif = fields.Date(string="Date de notification")
	dt_sign = fields.Date(string="Date de signature (Approuvé le)")
	dt_clot = fields.Date(string="Date de cloture")
	id_dest = fields.Char(string="ID destinataire", size = 6)
	typ_dest = fields.Char(string="Type destinataire", size = 1)
	no_ifu = fields.Char(string="N° IFU", size = 11)
	mnt_vbp = fields.Integer(string ="Montant VBP", size = 15)
	mnt_ecp = fields.Integer(string ="Montant ECP", size = 15)
	mnt_ord = fields.Integer(string ="Montant ORD", size = 15)
	mnt_ex_tresor = fields.Integer(string ="Montant Exo Tresor", size = 15)
	ty_ap = fields.Char(string="Type ap")
	bank_id = fields.Many2one("res.partner.bank", string = "Banque")
	agence_bank_id = fields.Char(string = "N° Agence")
	acc_number = fields.Many2one("res.partner.bank", string = "N° compte")
	nm_titulaire = fields.Many2one("res.partner.bank", string = "Titulaire du comp")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one("ref_structure") 
	cd_mode_mp_id = fields.Many2one("budg_modemarche",  string ="Mode")
	flag_actif = fields.Char(string = "Actif" )
	dt_delai = fields.Date(string="Delai d'exécution")
	nb_j_delai = fields.Integer(string="Nombre jours")
	nb_s_delai = fields.Integer(string="Nombre semaine")
	nb_m_delai = fields.Integer(string="Nombre mois")
	nb_a_delai = fields.Integer(string="Nombre année")
	dt_visa_dmp = fields.Date()
	dt_visa_daf = fields.Date()
	dt_visa_cf = fields.Date()
	dt_visa_ord = fields.Date()	
	cd_type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", string="Type de bénéficiaire")
	cd_type_financement_id = fields.Many2one("ref_bailleur", "Financement")
	beneficiaire_id = fields.Many2one("ref_beneficiaire", string="Bénéficiaire")
	#cd_nature_depense_id = fields.Many2one("budg_naturedepense", string="Nature")
	state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Confirmé'),
        ('V', 'Approuvé par DMP'),
		('A', 'Annulé'),
		('W', 'Visé par DAF'),
		('WCF', 'Visé par CF'),
		('WORD', 'Visé par ORD'),
        ], 'Etat', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
	
	_sql_constraints = [
        ('ref_mp', 'unique (ref_mp)', "Ce code existe déjà. Veuillez changer de code !"),
    ]

	@api.multi
	def action_marche_draft(self):
		self.write({'state': 'draft'})

	@api.multi
	def action_marche_confirmer(self):
		self.write({'state': 'N'})
		
	@api.multi
	def action_marche_approuver_dmp(self):
		self.write({'state': 'V'})
		
	@api.multi
	def action_marche_annuler(self):
		self.write({'state': 'A'})
		
	@api.multi
	def action_marche_viser_daf(self):
		self.write({'state': 'W'})
		
	@api.multi
	def action_marche_viser_cf(self):
		self.write({'state': 'WCF'})
		
	@api.multi
	def action_marche_viser_ord(self):
		self.write({'state': 'WORD'})

	@api.onchange('id_ao')

	def id_ao_on_change(self):

		if self.id_ao:
			self.ref_mp = self.id_ao.ref_ao
			self.cd_section_id = self.id_ao.cd_section_id
			#self.cd_nature_depense_id = self.id_ao.cd_nature_depense_id
			self.cd_type_financement_id = self.id_ao.cd_bailleur_id
			self.cd_mode_mp_id = self.id_ao.cd_mode_mp_id
			
			
class BudgContratService(models.Model):
	
	_name = 'budg_contrat_service'
	
	origine = fields.Char("Origine contrat")
	reference = fields.Char("Référence")
	nature_contrat = fields.Char("Nature contrat")
	#nature_depense = fields.Many2one("budg_naturedepense", "Nature dépense")
	mnt_disponible = fields.Integer("Info créd. dispo")
	mnt_contrat = fields.Integer("Montant contrat")
	id_appel = fields.Many2one("budg_appeloffre", "Identifiant Appel/Demande")
	mode_passation = fields.Many2one("budg_modemarche", "Mode de passation")
	financement_id = fields.Many2one("ref_bailleur", "Financement")
	type_beneficiaire = fields.Many2one("ref_typebeneficiaire", "Type Bénéficiaire")
	beneficiaire_id = fields.Many2one("ref_beneficiaire", string="Identité")
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", string = "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", required=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", required=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", required=True)
	objet_contrat = fields.Text("Objet contrat")
	dt_notif = fields.Date(string="Notifié le")
	dt_sign = fields.Date(string="Signé le")
	dt_clot = fields.Date(string="Clôturé le")
	dt_exec = fields.Date(string="Exécuté le")
	nb_j_delai = fields.Integer(string="Nombre jours")
	nb_s_delai = fields.Integer(string="Nombre semaine")
	nb_m_delai = fields.Integer(string="Nombre mois")
	nb_a_delai = fields.Integer(string="Nombre année")
	etat = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Confirmé'),
        ('V', 'Approuvé par DMP'),
		('A', 'Annulé'),
        ], 'Etat', default='draft')
	
	@api.multi
	def action_draft(self):
		self.write({'etat': 'draft'})

	@api.multi
	def action_confirmer(self):
		self.write({'etat': 'N'})
		
	@api.multi
	def action_approuver(self):
		self.write({'etat': 'V'})
		
	@api.multi
	def action_annuler(self):
		self.write({'etat': 'A'})
	

class BudgBudget(models.Model):

	_name = "budg_budget"
	_rec_name = "refp"

	name = fields.Char(string="Nom")
	typebudget_id = fields.Many2one("budg_typebudget", string = "Type de Budget", required=True)
	cd_type_piece_budget = fields.Many2one("budg_typepiecebudget", string = "Type de Pièce", required=True)
	refp = fields.Char(string = "Ref.Piece", required=True)
	date_to = fields.Date(string = "Date de mise en place", required=True)	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	dots_titre1 = fields.Float("RECETTES", compute="compute_dotation_titre1")
	dots_titre2 = fields.Float("DEPENSES", compute="compute_dotation_titre2")
	#sum_titre = fields.Integer("Titre")
	ecarts = fields.Float("ECART", compute="compute_ecart")
	dot_titre1section1 = fields.Float("Recettes/Fonctionnement", compute="compute_dotation_titre1section1")
	dot_titre1section2 = fields.Float("Recettes/Investissements", compute="compute_dotation_titre1section2")
	dot_titre2section1 = fields.Float("Dépenses/Fonctionnement", compute="compute_dotation_titre2section1")
	dot_titre2section2 = fields.Float("Dépenses/Investissements", compute="compute_dotation_titre2section2")
	dot_titre1section1chapitre = fields.Float("Titre I/Sect I/Chap", compute="compute_dotation_titre1section1chapitre")
	sum_titre = fields.Float("TITRES")
	dot_titre1section2chapitre = fields.Float("Titre I/Sect II/Chap")
	fichier_joint = fields.Binary(string="Joindre l'acte", attachment=True)
	rubrique_ids = fields.One2many("budg_ligne_budgetaire","budg_id")
	state = fields.Selection([
        ('AP', 'Avant projet'),
        ('N', 'Projet'),
        ('E', 'Exécutoire')
        ], 'Etat', default='AP', index=True, required=True, readonly=True, copy=False, track_visibility='always')

	
	#fonction de controle du type de budget	pour empecher la double saisie du budget primitif
	@api.onchange('typebudget_id')
	def controle_type_budget(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		self.env.cr.execute("select count(b.id) FROM budg_budget b, budg_typebudget t, ref_exercice r WHERE b.x_exercice_id = %d AND b.company_id = %d and t.id = b.typebudget_id AND t.cd_type_budget = 'BI' " %(val_ex, val_struct))
		res = self.env.cr.fetchone()
		val = res and res[0]
		if val > 0 and self.typebudget_id.cd_type_budget == 'BI':
			raise ValidationError(_('Le budget initial' + " " +  str(self.x_exercice_id.no_ex) + " " + 'est déjà saisie'))
		
	"""	
	@api.onchange('date_to')
	def controle_date(self):
		
		val_date = date.today()
		if self.date_to < val_date:
	
	
	@api.model
	def init(self):
		
		val_id = self.id
		val_ex = self.x_exercice_id
		val_struct = self.company_id
		
		tools.drop_view_if_exists(self.env.cr, 'vue_nature')
        self.env.cr.execute(" CREATE OR REPLACE VIEW W_BUDGET AS (
        SELECT t.cd_titre, t.lb_long, s.cd_section, s.lb_long, c.cd_chapitre, c.lb_long,a.cd_article, a.lb_long,p.cd_paragraphe, p.lb_long,r.rubrique, r.lb_long,
			l.mnt_ant1,l.mnt_ant2,l.mnt_precedent, l.mnt_budgetise 
		FROM ref_titre t, ref_section s, ref_chapitre c, ref_article a, ref_paragraphe p, budg_rubrique r,
			budg_titre bt, budg_section bs, budg_chapitre bc, budg_article ba, budg_paragraphe bp, budg_budget bb, budg_ligne_budgetaire l
		WHERE t.id = bt.titre AND bt.id = l.cd_titre_id AND s.id = bs.section AND bs.id = l.cd_section_id AND c.id = bc.chapitre AND bc.id = l.cd_chapitre_id
			AND a.id = ba.article AND ba.id = l.cd_article_id AND p.id = bp.paragraphe AND bp.id = l.cd_paragraphe_id AND bb.id = %s AND 
			r.id = l.cd_rubrique_id AND bb.x_exercice_id = %s AND bb.company_id = %s
			group by t.cd_titre, t.lb_long, s.cd_section, s.lb_long, c.cd_chapitre, c.lb_long,a.cd_article, a.lb_long,p.cd_paragraphe, p.lb_long,r.rubrique, r.lb_long,
			l.mnt_ant1,l.mnt_ant2,l.mnt_precedent, l.mnt_budgetise order by t.cd_titre, s.cd_section, c.cd_chapitre, a.cd_article, p.cd_paragraphe, r.rubrique,
			l.mnt_ant1,l.mnt_ant2,l.mnt_precedent, l.mnt_budgetise
			)" %(val_id,val_ex,val_struct))
			
		raise ValidationError(_('La date de mise ne peut être supérieure à la date du jour.'))
	"""
	
	
		
	#fonction de validation et réaménagement budgetaire
	def validation_budget(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_budg = int(self.id)
	
		
		#recuperation des données des recettes
		self.env.cr.execute("""SELECT l.*
		FROM budg_ligne_budgetaire l, budg_titre t WHERE l.x_exercice_id = %d AND l.company_id = %d 
		AND l.budg_id = %d AND l.cd_titre_id = t.id AND t.type_titre = 'R' """ %(val_ex, val_struct, val_budg))
		for line in self.env.cr.dictfetchall():
			#print('ligne', line['mnts_budgetise'])
				
			v_titre = line['cd_titre_id']
			v_section = line['cd_section_id']
			v_chap = line['cd_chapitre_id']
			v_article =  line['cd_article_id']
			v_para = line['cd_paragraphe_id']
			v_rub =  line['cd_rubrique_id']
			mnt_budgetise = line['mnts_budgetise']
			
			#curseur pour compter le nombre de ligne de depense dans la ligne executoire des dépenses
			self.env.cr.execute("""SELECT coalesce(count(*),0) FROM budg_ligne_exe_rec 
				WHERE cd_titre_id = %d AND cd_section_id = %d AND cd_chapitre_id = %d AND cd_art_id = %d AND
				cd_paragraphe_id = %d AND cd_rubrique_id = %d AND x_exercice_id = %d AND company_id = %d """ %(v_titre,v_section,v_chap,v_article,v_para,v_rub,val_ex,val_struct))
			curs_verif_recette = self.env.cr.fetchone()[0] or 0
			print('nombre ligne de recette',curs_verif_recette)
				
			if curs_verif_recette == 0:
				self.env.cr.execute("""INSERT INTO budg_ligne_exe_rec (cd_titre_id, cd_section_id, cd_chapitre_id, cd_art_id, cd_paragraphe_id, cd_rubrique_id, mnt_budgetise,mnt_corrige, reste_emettre, company_id, x_exercice_id) 
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
				""" ,(v_titre, v_section, v_chap, v_article, v_para, v_rub, mnt_budgetise, mnt_budgetise,mnt_budgetise, val_struct, val_ex))
				
				#self.env.cr.execute("""INSERT INTO compta_cg_rec_line (cd_titre_id, cd_section_id, cd_chapitre_id, cd_art_id, cd_paragraphe_id, cd_rubrique_id, mnt_budgetise,mnt_corrige,rest_recouvrer, company_id, x_exercice_id, budg_id) 
				#VALUES (%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)  
				#""" %(v_titre, v_section, v_chap, v_article, v_para, v_rub, mnt_budgetise, mnt_budgetise,mnt_budgetise, val_struct, val_ex, val_budg))				
			else:
				self.env.cr.execute("""UPDATE budg_ligne_exe_rec SET mnt_corrige = coalesce((mnt_corrige),0) + %s, reste_emettre = coalesce((reste_emettre),0) + %s
				WHERE cd_titre_id = %s AND cd_section_id = %s AND  cd_chapitre_id = %s and  cd_art_id = %s and
				cd_paragraphe_id = %s AND cd_rubrique_id = %s AND x_exercice_id = %s AND company_id = %s """
				,(mnt_budgetise,mnt_budgetise,v_titre,v_section,v_chap,v_article,v_para,v_rub,val_ex,val_struct))			
		
				#self.env.cr.execute("""UPDATE compta_cg_rec_line SET mnt_corrige = mnt_corrige + %d
				#WHERE cd_titre_id = %d AND cd_section_id = %d AND  cd_chapitre_id = %d and  cd_art_id = %d and
				#cd_paragraphe_id = %d AND cd_rubrique_id = %d AND x_exercice_id = %d AND company_id = %d """
				#%(mnt_budgetise,v_titre,v_section,v_chap,v_article,v_para,v_rub,val_ex,val_struct))			
		
		#recuperation des données des dépenses
		self.env.cr.execute("""SELECT l.*
		FROM budg_ligne_budgetaire l, budg_titre t WHERE l.x_exercice_id = %d AND l.company_id = %d 
		and l.budg_id = %d AND l.cd_titre_id = t.id AND t.type_titre = 'D' """ %(val_ex, val_struct, val_budg))	
		for line in self.env.cr.dictfetchall():
				
			v_titre1 = line['cd_titre_id']
			v_section1 = line['cd_section_id']
			v_chap1 = line['cd_chapitre_id']
			v_article1 = line['cd_article_id']
			v_para1 = line['cd_paragraphe_id']
			v_rub1 = line['cd_rubrique_id']
			mnt_budgetise1 = line['mnts_budgetise']
		
			#curseur pour compter le nombre de ligne de depense dans la ligne executoire des dépenses
			self.env.cr.execute("""SELECT coalesce(count(*),0) FROM budg_ligne_exe_dep 
				WHERE cd_titre_id = %d AND cd_section_id = %d AND cd_chapitre_id = %d AND cd_art_id = %d AND
				cd_paragraphe_id = %d AND cd_rubrique_id = %d AND x_exercice_id = %d AND company_id = %d """ %(v_titre1,v_section1,v_chap1,v_article1,v_para1,v_rub1,val_ex,val_struct))
			curs_verif_depense = self.env.cr.fetchone()[0] or 0
			#curs_verif_depense = curs_verif_dep and curs_verif_dep[0]
			print('nombre ligne de depense',curs_verif_depense)
			
			if curs_verif_depense == 0:
				self.env.cr.execute("""INSERT INTO budg_ligne_exe_dep (cd_titre_id, cd_section_id, cd_chapitre_id, cd_art_id, cd_paragraphe_id, cd_rubrique_id, mnt_budgetise,mnt_corrige, mnt_disponible, reste_mandat, company_id, x_exercice_id) 
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
				""" ,(v_titre1, v_section1, v_chap1, v_article1, v_para1, v_rub1, mnt_budgetise1, mnt_budgetise1, mnt_budgetise1,mnt_budgetise1, val_struct, val_ex))
				
				#self.env.cr.execute("""INSERT INTO compta_cg_dep_line (cd_titre_id, cd_section_id, cd_chapitre_id, cd_art_id, cd_paragraphe_id, cd_rubrique_id, mnt_budgetise,mnt_corrige, company_id, x_exercice_id, budg_id) 
				#VALUES (%d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d) 
				#""" %(v_titre1, v_section1, v_chap1, v_article1, v_para1, v_rub1, mnt_budgetise1, mnt_budgetise1, val_struct, val_ex, val_budg))					
			else:
				self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET mnt_corrige = coalesce((mnt_corrige),0) + %s, mnt_disponible = coalesce((mnt_disponible),0) + %s, reste_mandat = coalesce((reste_mandat),0) + %s
				WHERE cd_titre_id = %s AND cd_section_id = %s AND  cd_chapitre_id = %s AND  cd_art_id = %s AND
				cd_paragraphe_id = %s AND cd_rubrique_id = %s AND x_exercice_id = %s AND company_id = %s """
				,(mnt_budgetise1,mnt_budgetise1,mnt_budgetise1,v_titre1,v_section1,v_chap1,v_article1,v_para1,v_rub1,val_ex,val_struct))
				
				#self.env.cr.execute("""UPDATE compta_cg_dep_line SET mnt_corrige = mnt_corrige + %d
				#WHERE cd_titre_id = %d AND cd_section_id = %d AND  cd_chapitre_id = %d AND  cd_art_id = %d AND
				#cd_paragraphe_id = %d AND cd_rubrique_id = %d AND x_exercice_id = %d AND company_id = %d """
				#%(mnt_budgetise1,v_titre1,v_section1,v_chap1,v_article1,v_para1,v_rub1,val_struct,val_ex))
	
	@api.multi
	def valider_avt_projet(self):
		self.write({'state': 'N'})
				
	@api.multi	
	def budget_valider(self):
		
		if (self.dots_titre1 - self.dots_titre2 == 0):
			self.validation_budget()
			self.write({'state': 'E'})
		else:
			raise ValidationError(_('Vous ne pouvez pas valider le budget car les dépenses et les recettes ne sont pas équilibrées.'))
		
	
		
	
	#function de calcul des agrégations des titres	
	@api.onchange('rubrique_ids.cd_titre_id')
	def compute_sum_titre(self):
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
			val_titre = int(self.rubrique_ids.cd_titre_id)
			
			result = self.env['budg_ligne_budgetaire'].search([('cd_titre_id','=',val_titre),('company_id','=',val_struct),('x_exercice_id','=',val_ex)])
			self.sum_titre = resultat.sum(mnt_budgetise)

	
	@api.one
	def compute_dotation_titre1(self):
		
		val_budg = (self.id)
		for val in self:
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
				
			val.env.cr.execute("select sum(l.mnts_budgetise) from ref_titre t, budg_titre bt, budg_ligne_budgetaire l where t.cd_titre = 'I' and t.id = bt.titre and bt.id = l.cd_titre_id  and l.x_exercice_id = %d and l.company_id = %d and budg_id = %d group by t.cd_titre" %(val_ex,val_struct, val_budg))
			res = self.env.cr.fetchone()
			self.dots_titre1 = res and res[0]
		
		
	@api.one
	def compute_dotation_titre2(self):
		
		val_budg = (self.id)
		
		for val in self:
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
				
			val.env.cr.execute("select sum(l.mnts_budgetise) from ref_titre t, budg_titre bt, budg_ligne_budgetaire l where t.cd_titre = 'II' and t.id = bt.titre and bt.id = l.cd_titre_id  and l.x_exercice_id = %d and l.company_id = %d and budg_id = %d group by t.cd_titre" %(val_ex,val_struct, val_budg))
			res = self.env.cr.fetchone()
			self.dots_titre2 = res and res[0]
	
	
	@api.one
	def compute_ecart(self):
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
			
			self.ecarts = self.dots_titre1 - self.dots_titre2
	
	
	@api.one
	def compute_dotation_titre1section1(self):
		
		val_budg = (self.id)
		
		for val in self:
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
				
			val.env.cr.execute("select sum(l.mnts_budgetise) from ref_exercice e,ref_titre t ,ref_section s INNER JOIN budg_ligne_budgetaire l ON s.id = l.cd_section_id where s.cd_section = 'I' and l.cd_titre_id =  t.id and t.cd_titre = 'I' and e.etat = 1 and l.x_exercice_id = %d and l.company_id = %d and budg_id = %s group by cd_section,l.cd_titre_id" %(val_ex,val_struct, val_budg))
			res = self.env.cr.fetchone()
			self.dot_titre1section1 = res and res[0]
		
		
	@api.one
	def compute_dotation_titre1section2(self):
		
		val_budg = (self.id)
		
		for val in self:
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
				
			self.env.cr.execute("select sum(l.mnts_budgetise) from ref_exercice e,ref_titre t ,ref_section s INNER JOIN budg_ligne_budgetaire l ON s.id = l.cd_section_id where s.cd_section = 'II' and l.cd_titre_id =  t.id and t.cd_titre = 'I'and e.etat = 1 and l.x_exercice_id = %d and l.company_id = %d and budg_id = %s group by cd_section,l.cd_titre_id" %(val_ex,val_struct, val_budg))
			res = self.env.cr.fetchone()
			self.dot_titre1section2 = res and res[0]
		
		
	@api.one
	def compute_dotation_titre2section1(self):
		
		val_budg = (self.id)
		
		for val in self:
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
				
			self.env.cr.execute("select sum(l.mnts_budgetise) from ref_exercice e,ref_titre t ,ref_section s INNER JOIN budg_ligne_budgetaire l ON s.id = l.cd_section_id where s.cd_section = 'I' and l.cd_titre_id =  t.id and t.cd_titre = 'II'and e.etat = 1 and l.x_exercice_id = %d and l.company_id = %d and budg_id = %s group by cd_section,l.cd_titre_id" %(val_ex,val_struct, val_budg))
			res = self.env.cr.fetchone()
			self.dot_titre2section1 = res and res[0]
		
		
	@api.one
	def compute_dotation_titre2section2(self):
		
		val_budg = (self.id)
		
		for val in self:
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
				
			self.env.cr.execute("select sum(l.mnts_budgetise) from ref_exercice e,ref_titre t ,ref_section s INNER JOIN budg_ligne_budgetaire l ON s.id = l.cd_section_id where s.cd_section = 'II' and l.cd_titre_id =  t.id and t.cd_titre = 'II' and e.etat = 1 and l.x_exercice_id = %d and l.company_id = %d and budg_id = %s group by cd_section,l.cd_titre_id" %(val_ex,val_struct, val_budg))
			res = self.env.cr.fetchone()
			self.dot_titre2section2 = res and res[0]
		
		
		
	@api.one
	def compute_dotation_titre1section1chapitre(self):
		
		val_budg = (self.id)
		
		for val in self:
		
			val_ex = int(self.x_exercice_id.id)
			val_struct = int(self.company_id.id)
				
			self.env.cr.execute("""select sum(l.mnts_budgetise) 
			from ref_exercice e,ref_titre t,ref_section s, ref_chapitre c INNER JOIN l ON c.id = l.cd_chapitre_id where s.id = c.cd_section_id 
			and s.cd_section = 'I'and t.id = s.cd_titre_id and t.cd_titre = 'I' and e.etat = 1 and l.x_exercice_id = %d and l.company_id = %d and budg_id = %s group by l.cd_chapitre_id""" %(val_ex,val_struct, val_budg))
			res = self.env.cr.fetchone()
			self.dot_titre1section1chapitre = res and res[0]
	
	
	def AfficherRubrique(self):
		
		v_struct = int(self.company_id)
		
		for vals in self:
			vals.env.cr.execute("""select cd_titre_id as tit, cd_section_id as sec, cd_chapitre_id as chap, cd_paragraphe_id as par, cd_article_id as art, id as rub
			from budg_rubrique where company_id = %d order by tit, sec, chap, par, art, id""" %(v_struct))
			rows = vals.env.cr.dictfetchall()
			result = []
            
			vals.rubrique_ids.unlink()
			for line in rows:
				result.append((0,0, {'cd_titre_id' : line['tit'],'cd_section_id' : line['sec'],'cd_chapitre_id' : line['chap'],'cd_paragraphe_id' : line['par'],'cd_article_id' : line['art'],'cd_rubrique_id' : line['rub']}))
			self.rubrique_ids = result
			
			
class BudgLigneBudgetaire(models.Model):

	_name = "budg_ligne_budgetaire"

	budg_id = fields.Many2one("budg_budget", ondelete='cascade')
	cd_titre_id = fields.Many2one("budg_titre", string = "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section", string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", required=False)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", required=False)
	mnts_ant1 = fields.Float(string = "Ex n-3 Prévision", readonly=True)
	mnts_ant1exe = fields.Float(string = "Ex n-3 Exécution", readonly=True)
	mnts_ant2 = fields.Float(string = "EX n-2 Prévision", readonly=True)
	mnts_ant2exe = fields.Float(string = "Ex n-2 Exécution", readonly=True)
	mnts_precedent = fields.Float(string = "Ex n-1 Prévision", readonly=True)
	mnts_precedentexe = fields.Float(string = "Ex n-1 Exécution", readonly=True)
	mnts_budgetise = fields.Float("Montant budgétisé", required=False)
	mnt_ant1 = fields.Float(string = "Ex n-3")
	mnt_ant2 = fields.Float(string = "EX n-2")
	mnt_precedent = fields.Float(string = "Ex n-1")
	mnt_budgetise = fields.Float("Montant budgétisé")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	fg_rea = fields.Boolean('OK ?', default = False)
	
	@api.onchange('cd_titre_id', 'cd_section_id', 'cd_chapitre_id','cd_article_id','cd_paragraphe_id','cd_rubrique_id')
	def valprec(self):
		v_titre = int(self.cd_titre_id)
		v_section = int(self.cd_section_id)
		v_chap = int(self.cd_chapitre_id)
		v_art = int(self.cd_article_id)
		v_para = int(self.cd_paragraphe_id)
		v_rub = int(self.cd_rubrique_id)
		v_exercice = int(self.x_exercice_id)
		v_exe = int(self.x_exercice_id.no_ex)
		v_exe1 = int(v_exe) - 1
		v_ex = int(v_exe1)
		v_exe2 = int(v_exe) - 2
		v_ex2 = int(v_exe2)
		v_exe3 = int(v_exe) - 3
		v_ex3 = int(v_exe3)
		v_com = int(self.company_id)
		
		for record in self:
		
			self.env.cr.execute("""select mnts_budgetise from budg_ligne_budgetaire l, ref_exercice r where l.cd_titre_id = %d and cd_section_id = %d and l.cd_chapitre_id = %d
			and l.cd_article_id = %d and l.cd_paragraphe_id = %d and l.cd_rubrique_id = %d and 
			l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_titre, v_section, v_chap, v_art, v_para, v_rub, v_com, v_ex))
	
			mnt = self.env.cr.fetchone()
			self.mnts_precedent = mnt and mnt[0] or 0
			
		
		for record in self:
		
			self.env.cr.execute("""select mnts_budgetise from budg_ligne_budgetaire l, ref_exercice r where l.cd_titre_id = %d and cd_section_id = %d and l.cd_chapitre_id = %d
			and l.cd_article_id = %d and l.cd_paragraphe_id = %d and l.cd_rubrique_id = %d and 
			l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_titre, v_section, v_chap, v_art, v_para, v_rub, v_com, v_ex2))
			
			mnt = self.env.cr.fetchone()
			self.mnts_ant2 = mnt and mnt[0] or 0

		
		for record in self:
		
			self.env.cr.execute("""select mnts_budgetise from budg_ligne_budgetaire l, ref_exercice r where l.cd_titre_id = %d and cd_section_id = %d and l.cd_chapitre_id = %d
			and l.cd_article_id = %d and l.cd_paragraphe_id = %d and l.cd_rubrique_id = %d and 
			l.company_id = %d and cast(r.no_ex as int) = %d""" %(v_titre, v_section, v_chap, v_art, v_para, v_rub, v_com, v_ex3))
	
			mnt = self.env.cr.fetchone()
			self.mnts_ant1 = mnt and mnt[0] or 0
	
	
	@api.onchange('cd_paragraphe_id')
	def Rub(self):

		for x in self:
			x.cd_titre_id = x.cd_paragraphe_id.cd_titre_id
			x.cd_section_id = x.cd_paragraphe_id.cd_section_id
			x.cd_chapitre_id = x.cd_paragraphe_id.cd_chapitre_id
			x.cd_article_id = x.cd_paragraphe_id.cd_article_id
			#x.cd_paragraphe_id = x.cd_rubrique_id.cd_paragraphe_id
	
			

class BudgActReamenagement(models.Model):
	_name = "budg_act_reamenagement"
	
	name = fields.Char("")

class BudgPieceEng(models.Model):
	_name = "budg_piece_engagement"
	
	lb_long = fields.Many2one("budg_typepjbudget", "Libellé", required=True)
	oblige = fields.Boolean("Obligatoire")
	nombre = fields.Integer("Nombre")
	ref = fields.Char("Référence", required=True)
	montant = fields.Integer("Montant")
	dte = fields.Date("Date")
	eng_id = fields.Many2one("budg_engagement", ondelete='cascade')
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	

class BudgPieceLiq(models.Model):
	_name = "budg_piece_liq"
	
	lb_long = fields.Many2one("budg_typepjbudget", "Libellé")
	oblige = fields.Boolean("Obligé")
	nombre = fields.Integer("Nombre")
	ref = fields.Char("Référence")
	dte = fields.Date("Date")
	montant = fields.Integer("Montant")
	liq_id = fields.Many2one("budg_liqord", ondelete='cascade')
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	

class BudgPieceOrd(models.Model):
	_name = "budg_piece_ord"
	
	lb_long = fields.Many2one("budg_typepjbudget", "Libellé")
	oblige = fields.Boolean("Obligé")
	nombre = fields.Integer("Nombre")
	ref = fields.Char("Référence")
	dte = fields.Date("Date")
	montant = fields.Integer("Montant")
	mandat_id = fields.Many2one("budg_mandat", ondelete='cascade')
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	

class BudgPieceRec(models.Model):
	_name = "budg_piece_recette"
	
	lb_long = fields.Many2one("budg_typepjbudget", "Libellé")
	oblige = fields.Boolean("Obligé")
	nombre = fields.Integer("Nombre")
	ref = fields.Char("Référence")
	montant = fields.Integer("Montant")
	recette_id = fields.Many2one("budg_titrerecette", ondelete='cascade')
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	

class BudgEngagement(models.Model):

	_name = "budg_engagement"
	_rec_name = "no_eng"
	_order = "id desc"

	name = fields.Char(string="Nom")
	no_eng = fields.Char(string="N° engagement", readonly=True)
	cd_titre_id = fields.Many2one("budg_titre",default=lambda self: self.env['budg_titre'].search([('type_titre','=', 'D')]), string = "Titre", required=True, readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", required=True, states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)],'L': [('readonly', True)],'O': [('readonly', True)]})
	lbsection = fields.Char()
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", required=True, states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", required=True, states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", required=True, states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", required=True, states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	type_procedure = fields.Many2one("budg_typeprocedure", string = "Type de procédure", required=True, states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	#cd_type_depense = fields.Many2one("budg_typedepense", string = "Type de dépense", required=True, states={'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	type_budget_id = fields.Many2one("budg_typebudget", string = "Type de budget", states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", required=True, string = "Catégorie", states={'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	categorie_beneficiaire_id = fields.Many2one("ref_categoriebeneficiaire", string = "Cate de bénéf/four")
	no_beneficiaire = fields.Many2one("ref_beneficiaire", required=True, string = "Identité", states={'V': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	nature_dep = fields.Many2one("ref_article", string = "Nature de dépense", required=False, states={'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	no_bord_eng = fields.Many2one("budg_bordereau_engagement", string = "N° bordereau engagement")
	no_grpadm = fields.Char(string = "N° GRPADM")
	typedossier = fields.Many2one("budg_typedossierbudg",default=lambda self: self.env['budg_typedossierbudg'].search([('code','=', 'ENG')]), string = "Type de dossier",  readonly=True,)
	no_grpadm_pere = fields.Char(string = "N° GRPADM PERE")
	lb_obj = fields.Text(string = "Objet",size=300, required=True)
	mnt_init_eng = fields.Float(string = "Montant initiale engagé", digits = (20,0), compute="mnt_init_eng")
	credit_eng = fields.Float(string = "Montant initiale engagé", digits = (20,0))
	mnt_eng = fields.Float(string = "Montant engagement", digits = (20,0), required=True, states={'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	mnt_liq = fields.Float(string = "Montant liquidé", digits = (20,0))
	credit_dispo = fields.Float(string = "Crédit disponible", digits = (20,0), readonly=True, states={'R': [('readonly', True)],'W': [('readonly', True)], 'V': [('readonly', True)], 'L': [('readonly', True)],'O': [('readonly', True)]})
	nb_pjust = fields.Integer(string = "Nombre piece justi.")
	piecejust_ids = fields.One2many("budg_piece_engagement",'eng_id')
	dt_visa_cf = fields.Date(string = "Date Visa")
	cpte_benef = fields.Char('compte')
	imput_benef = fields.Char('imput')
	cpte_rub = fields.Char('compte rub')
	modereg = fields.Many2one('ref_modereglement', 'Mode de règlement')
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date", required =True)
	nb_edit = fields.Integer(string = "nb_edit")
	mnt_lbudg_ap = fields.Float(string = "Montant ligne budgetaire ap")
	mnt_period_ap = fields.Float(string = "Montant periode ap", digits = (20,0))
	mnt_ord = fields.Float(string = "Montant ordonnancé", digits = (20,0))
	mnt_annule = fields.Float(string = "Montant annulé", digits = (20,0))
	mnt_tot_eng = fields.Float(string = "Montant total engagé", digits = (20,0))
	cumul = fields.Float(string='Cumul')
	no_cpt_bp = fields.Integer(string = "Montant ecp")
	id_mp = fields.Char(string = "id mp")
	ref_mp = fields.Many2one("budg_marche",string = "Réf. Marché")
	motif_rejet = fields.Selection([('1', 'Erreur Imputation'),
		('2','Erreur Montant'),('3','Erreur Pièce'),('4','Erreur Bénéficiaire'),
		('5','Erreur Objet')],string = "Motif du rejet")
	bank_id = fields.Many2one("res.bank", string = "Banque")
	agence_bank_id = fields.Char(string = "N° Agence")
	acc_number = fields.Many2one("res.partner.bank", string = "N° compte")
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	fg_blocedit = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	user_id = fields.Many2one('res.users', string='user', track_visibilty='onchange', readonly=True,  default=lambda self: self.env.user)
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Confirmé'),
        ('V', 'Approuvé'),
		('A', 'Annulé'),
		#('W', 'Visé'),
		('R', 'Rejeté'),
		('LC', 'Liquidation en cours'),
		('L', 'Liquidé')
        ], 'Etat', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
	credit_disponible = fields.Float()
	envoyer_daf = fields.Selection([('Y','Oui'), ('N','Non')], default='N')
	reste = fields.Float()
	signataire_dfc1 = fields.Many2one("budg_signataire", default=lambda self: self.env['budg_signataire'].search([('code','=', 'DFC')]))
	signataire_dg1 = fields.Many2one("budg_signataire", default=lambda self: self.env['budg_signataire'].search([('code','=', 'DG')]))
	
	@api.onchange('cd_section_id')
	def OnchangeSection(self):
		
		if self.cd_section_id:
			self.lbsection = self.cd_section_id.section.lb_court
	
	@api.depends('mnt_eng')
	def amount_to_words(self):
		self.text_amount = num2words(self.mnt_eng, lang='fr')
   
	def afficher_piece(self):
        
		val_ex = int(self.x_exercice_id)
		categorie = int(self.categorie_beneficiaire_id)
		val_proc = int(self.type_procedure)
		val_doc = int(self.typedossier)
		titre = int(self.cd_titre_id)
		section = int(self.cd_section_id)
		chapitre = int(self.cd_chapitre_id)
		article = int(self.cd_article_id)
		paragraphe = int(self.cd_paragraphe_id)
		


		for vals in self:
		    vals.env.cr.execute("""select b.lb_long as lib, b.oblige as obl, b.nombre as nbr from budg_pj_dep b, budg_naturedepense n where n.cd_type_dossier_id = %d and n.type_procedure_id = %d and n.cat_benef = %d
			and n.cd_titre_id = %d and n.cd_section_id = %d and n.cd_chapitre_id = %d and n.cd_article_id = %d and n.cd_paragraphe_id = %d 
			and n.id = b.nature_dep_id""" %(val_doc,val_proc,categorie,titre, section, chapitre, article, paragraphe))
		    rows = vals.env.cr.dictfetchall()
		    result = []
		    
		    vals.piecejust_ids.unlink()
		    for line in rows:
		        result.append((0,0, {'lb_long' : line['lib'], 'oblige': line['obl'], 'nombre': line['nbr']}))
		    self.piecejust_ids = result
  
  
		
	@api.onchange('type_beneficiaire_id')
	def cpte(self):
		#self.cpte_benef = self.type_beneficiaire_id.cpte_client.souscpte.concate_souscpte
		#self.imput_benef = self.type_beneficiaire_id.cpte_client.souscpte.id
		#self.categorie_beneficiaire_id = self.type_beneficiaire_id.cat_id
		
		self.cpte_benef = self.type_beneficiaire_id.cpte_client.souscpte.concate_souscpte
		self.imput_benef = self.type_beneficiaire_id.cpte_client.souscpte.id
	
	
	@api.onchange('cd_rubrique_id')
	def cpterub(self):
		self.cpte_rub = self.cd_rubrique_id.no_imputation.souscpte.concate_souscpte

	@api.multi
	def action_eng_draft(self):
		self.write({'state': 'draft'})

	@api.multi
	def action_eng_confirmer(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_rub = int(self.cd_rubrique_id)
		val_par = int(self.cd_paragraphe_id)
		val_art = int(self.cd_article_id)
		val_sec = int(self.cd_section_id)
		val_chap = int(self.cd_chapitre_id)
		val_titre = int(self.cd_titre_id)
		v_id = int(self.id)
		
		self.write({'state': 'N'})
		
	
		self.env.cr.execute("select noeng from budg_compteur_eng where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct) )
		eng = self.env.cr.fetchone()
		no_eng = eng and eng[0] or 0
		c1 = int(no_eng) + 1
		c = str(no_eng)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_eng = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_eng(x_exercice_id,company_id,noeng)  VALUES(%d ,%d, %d)""" %(val_ex, val_struct,vals))	
		else:
			c1 = int(no_eng) + 1
			c = str(no_eng)
			ok = str(c1).zfill(4)
			self.no_eng = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_eng SET noeng = %d WHERE x_exercice_id = %d and company_id = %d" %(vals, val_ex, val_struct))
		
		self.env.cr.execute("select distinct l.mnt_disponible from budg_ligne_exe_dep l where l.cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d" %(val_rub, val_ex, val_struct))
		res = self.env.cr.fetchone()[0] or 0
		
		if self.mnt_eng > res:
			raise ValidationError(_("Le montant de l'engagement est supérieur au montant budgétisé"))
	
		
		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET mnt_engage = (select sum(mnt_eng)
		FROM  budg_engagement WHERE cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d
		and cd_article_id = %d and cd_paragraphe_id = %d and cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d)
		WHERE cd_titre_id = %d AND cd_section_id = %d AND cd_chapitre_id = %d AND cd_art_id = %d AND cd_paragraphe_id = %d AND cd_rubrique_id = %d and company_id = %d and x_exercice_id = %d""" %(val_titre, val_sec, val_chap ,val_art, val_par,val_rub,val_struct,val_ex,val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_struct, val_ex))
		
		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET mnt_disponible = (mnt_corrige - mnt_engage)
		WHERE cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d and 
		cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d """ %(val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct))
				
		
		self.reste = self.mnt_eng
        
		self.credit_ouvert()
		self.cumul_anterieur()
		self.mnt_nvo_dispo()
		self.mnt_sum_eng()
		self.credits_disponible()
				
	
	def credit_ouvert(self):
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_rub = int(self.cd_rubrique_id)
		val_par = int(self.cd_paragraphe_id)
		val_art = int(self.cd_article_id)
		val_sec = int(self.cd_section_id)
		val_chap = int(self.cd_chapitre_id)
		val_titre = int(self.cd_titre_id)
		
		self.env.cr.execute("""select mnt_corrige from budg_ligne_exe_dep where cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d
		and cd_paragraphe_id = %d and cd_rubrique_id = %d and company_id = %d and x_exercice_id = %d"""
		%(val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_struct,val_ex))	
		
		res = self.env.cr.fetchone()
		self.credit_eng = res and res[0] or 0
		
	#@api.multi
	def cumul_anterieur(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_rub = int(self.cd_rubrique_id)
		val_para = int(self.cd_paragraphe_id)
		v_eng = str(self.no_eng)
	
		self.env.cr.execute("""select sum(e.mnt_eng) FROM budg_engagement e
		where cd_paragraphe_id = %d and cd_rubrique_id = %d and company_id = %d 
		and x_exercice_id = %d """ %(val_para, val_rub, val_struct, val_ex))
		
		res = self.env.cr.fetchone()
		r1 = res and res[0] or 0
		
		self.env.cr.execute("""select sum(e.mnt_eng) FROM budg_engagement e
		where cd_paragraphe_id = %s and cd_rubrique_id = %s and company_id = %s
		and x_exercice_id = %s and no_eng = %s """ ,(val_para, val_rub, val_struct, val_ex, v_eng))
		
		res1 = self.env.cr.fetchone()
		r2 = res1 and res1[0] or 0
		
		self.cumul = r1 - r2
		
	
	def mnt_nvo_dispo(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_art = int(self.cd_article_id)
		val_rub = int(self.cd_rubrique_id)
		val_para = int(self.cd_paragraphe_id)
		
		val_sec = int(self.cd_section_id)
		val_chap = int(self.cd_chapitre_id)
		val_titre = int(self.cd_titre_id)
	
		self.env.cr.execute("""select (mnt_corrige - mnt_engage) FROM budg_ligne_exe_dep
		WHERE company_id = %d and x_exercice_id = %d and cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d
		and cd_art_id = %d and cd_paragraphe_id = %d and cd_rubrique_id = %d
		""" %(val_struct,val_ex, val_titre, val_sec, val_chap, val_art, val_para, val_rub))
		
		res = self.env.cr.fetchone()
		self.mnt_lbudg_ap = res and res[0] or 0
		
	
	def mnt_sum_eng(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_rub = int(self.cd_rubrique_id)
		val_para = int(self.cd_paragraphe_id)
	
		self.env.cr.execute("""select sum(e.mnt_eng) FROM budg_engagement e
				WHERE e.cd_paragraphe_id = %d and cd_rubrique_id = %d
				and e.company_id = %d and e.x_exercice_id = %d""" %(val_para, val_rub, val_struct, val_ex))
		res = self.env.cr.fetchone()
		self.mnt_tot_eng = res and res[0] or 0

	def credits_disponible(self):
		for val in self:
			self.credit_disponible = self.credit_eng - self.cumul
	

	@api.multi
	def action_eng_approuver(self):
		#if self.type_procedure.type_procedure == '001':
		self.write({'state': 'V'})
		#else:
		#	self.write({'state':'W'})
	
	@api.multi
	def action_eng_annuler(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_id = str(self.no_eng)
		id_eng = int(self.id)
		val_para = int(self.cd_paragraphe_id)
		val_rub = int(self.cd_rubrique_id)
		self.write({'state': 'A'})
		self.mnt_annule = self.mnt_eng
		
		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET mnt_disponible = mnt_disponible + (select DISTINCT LED.mnt_eng FROM budg_engagement LED 
		WHERE LED.cd_paragraphe_id = %d and LED.cd_rubrique_id = %d and LED.company_id = %d and LED.x_exercice_id = %d and id = %d)
		WHERE cd_paragraphe_id = %d and cd_rubrique_id = %d and company_id = %d and x_exercice_id = %d""" %(val_para, val_rub, val_struct, val_ex,id_eng, val_para, val_rub, val_struct, val_ex))

		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET reste_mandat = reste_mandat + (select DISTINCT LED.mnt_ord FROM budg_mandat LED 
		WHERE LED.cd_paragraphe_id = %s and LED.cd_rubrique_id = %s and LED.company_id = %s and LED.x_exercice_id = %s and no_eng = %s)
		WHERE cd_paragraphe_id = %s and cd_rubrique_id = %s and company_id = %s and x_exercice_id = %s""" , (val_para, val_rub, val_struct, val_ex,val_id, val_para, val_rub, val_struct, val_ex))

	@api.multi
	def action_eng_viser(self):
		self.write({'state': 'W'})
		
	@api.multi
	def action_eng_rejeter(self):
		
		#if self.motif_rejet == '1':
		self.write({'state': 'R'})
		

	@api.onchange('cd_rubrique_id', 'cd_paragraphe_id', 'cd_article_id', 'cd_chapitre_id', 'cd_section_id', 'cd_titre_id')
	def cred_dipso(self):
		
		val_ex = int(self.x_exercice_id.id)
		val_struct = int(self.company_id.id)
		val_para = int(self.cd_paragraphe_id)
		val_rubrique = int(self.cd_rubrique_id)
		val_chap = int(self.cd_chapitre_id)
		val_sec = int(self.cd_section_id)
		val_tit = int(self.cd_titre_id)
		val_art = int(self.cd_article_id)
		
		result = self.env['budg_ligne_exe_dep'].search([('cd_titre_id','=',val_tit),('cd_section_id','=',val_sec),('cd_chapitre_id','=',val_chap),('cd_art_id','=',val_art),('cd_paragraphe_id','=',val_para),('cd_rubrique_id','=',val_rubrique),('company_id','=',val_struct),('x_exercice_id','=',val_ex)])

		self.credit_dispo = result.mnt_disponible
		
		
class Budg_Compteur_enga(models.Model):
	
	_name = "budg_compteur_eng"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	noeng = fields.Integer(default = 0)


class BudgLexedepense(models.Model):

	_name = "budg_ligne_exe_dep"

	cd_titre_id = fields.Many2one("budg_titre",string = "Titre")
	cd_section_id = fields.Many2one("budg_section",string = "Section")
	cd_chapitre_id = fields.Many2one("budg_chapitre",string = "Chapitre")
	cd_art_id = fields.Many2one("budg_param_article", string = "Article")
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe")
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique")
	mnt_budgetise = fields.Float(string = "Dotation initiale")
	mnt_corrige = fields.Float(string = "Dotation corrigée")
	mnt_engage= fields.Float(string = "Engagement")
	mnt_cf = fields.Float(string = "Montant CF")
	mnt_liquide = fields.Float(string = "Montant liquidé")
	mnt_mandate = fields.Float(string = "Mandatement")
	mnt_vbp = fields.Float(string = "Montant vbp")
	mnt_ecp = fields.Float(string = "Montant ecp")
	mnt_paye = fields.Float(string = "Montant payé")
	mnt_max_engage= fields.Float(string = "Montant maximum engagé")
	fg_bloc = fields.Selection([('oui','Oui'), ('non','Non')])
	dt_bloc = fields.Date()
	dt_fin_bloc = fields.Date()
	no_period = fields.Integer()
	mnt_period = fields.Integer()
	mnt_bloque = fields.Integer()
	fg_mnt_bloque = fields.Char()
	dt_deb_mnt_bloque = fields.Date()
	dt_fin_mnt_bloque = fields.Date()
	mnt_disponible = fields.Float("Disponible")
	reste_mandat = fields.Float("Reste à mandater")
	taux = fields.Float("Taux de réalisation(%)")
	mnt_precedent = fields.Float()
	mnt_anterieur1 = fields.Float()
	mnt_anterieur2 = fields.Float()
	budg_id = fields.Many2one("budg_budget")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

	"""
	@api.multi
	def _taux_depense(self):
		
		for line in self:
			if line.mnt_budgetise != 0:
				line.taux = float(line.mnt_engage / line.mnt_budgetise) * 100
			else:
				line.percentage = 0.00
	"""
	
class BudgLexerecette(models.Model):

	_name = "budg_ligne_exe_rec"


	cd_titre_id = fields.Many2one("budg_titre",string = "Titre")
	cd_section_id = fields.Many2one("budg_section",string = "Section")
	cd_chapitre_id = fields.Many2one("budg_chapitre",string = "Chapitre")
	cd_art_id = fields.Many2one("budg_param_article", string = "Article")
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe")
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique")
	mnt_budgetise = fields.Float(string = "Dotation initiale")
	mnt_corrige = fields.Float(string = "Dotation corrigée")
	mnt_emis= fields.Float(string = "Emission")
	mnt_cf = fields.Float(string = "Montant CF")
	mnt_liquide = fields.Float(string = "Montant ordonnancé")
	mnt_ord = fields.Float(string = "Montant mandaté")
	mnt_vbr = fields.Float(string = "Montant vbp")
	mnt_ecr = fields.Float(string = "Montant ecp")
	mnt_rec = fields.Float(string = "Titre émis")
	reste_emettre = fields.Float(string = "Reste à recouvrer")
	mnt_max_engage= fields.Float(string = "Montant maximum engagé",)
	taux = fields.Float("Taux de réalisation(%)")
	no_period = fields.Float()
	mnt_period = fields.Float()
	mnt_precedent = fields.Float()
	mnt_anterieur1 = fields.Float()
	mnt_anterieur2 = fields.Float()
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	budg_id = fields.Many2one("budg_budget")

	"""
	@api.multi
	def _taux_recette(self):
		
		for line in self:
			if line.mnt_budgetise != 0:
				line.taux = float(line.mnt_rec / line.mnt_budgetise) * 100
			else:
				line.percentage = 0.00
	"""	

class Budg_CA(models.Model):
	_name='budg_ca_dep'
	
	compte_admin = fields.Selection([		
		('D', 'Dépenses'),
		],default="D", string='Compte de gestion')
	dt_deb = fields.Date('Du')
	dt_fin = fields.Date('Au')
	ca_lines = fields.One2many("budg_ca_line_dep", "ca_id")


class Budg_CaLineDep(models.Model):
	_name='budg_ca_line_dep'
	
	ca_id = fields.Many2one("budg_ca_dep")
	cd_titre_id = fields.Char(string = "Titre")
	cd_section_id = fields.Char(string = "Section")
	cd_chapitre_id = fields.Char(string = "Chapitre")
	cd_art_id = fields.Char(string = "Article")
	cd_paragraphe_id = fields.Char(string = "Paragraphe")
	cd_rubrique_id = fields.Char(string = "Rubrique")
	mnt_budgetise = fields.Integer(string = "Dotation initiale", size = 15)
	mnt_corrige = fields.Integer(string = "Dotation corrigée", size = 15)
	mnt_engage= fields.Integer(string = "Engagement", size = 15)
	mnt_mandat= fields.Integer(string = "Mandatement", size = 15)
	mnt_dispo= fields.Integer(string = "Disponible", size = 15)
	taux = fields.Float(string = "Taux d'exécution")
	

class Budg_CA(models.Model):
	_name='budg_ca_rec'
	
	compte_admin = fields.Selection([		
		('R', 'Recettes'),
		],default="R", string='Compte administratif')
	dt_deb = fields.Date('Du')
	dt_fin = fields.Date('Au')
	ca_lines = fields.One2many("budg_ca_line_rec", "ca_id")


class Budg_CaLineDep(models.Model):
	_name='budg_ca_line_rec'
	
	ca_id = fields.Many2one("budg_ca_rec")
	cd_titre_id = fields.Char(string = "Titre")
	cd_section_id = fields.Char(string = "Section")
	cd_chapitre_id = fields.Char(string = "Chapitre")
	cd_art_id = fields.Char(string = "Article")
	cd_paragraphe_id = fields.Char(string = "Paragraphe")
	cd_rubrique_id = fields.Char(string = "Rubrique")
	mnt_budgetise = fields.Integer(string = "Dotation initiale", size = 15)
	mnt_corrige = fields.Integer(string = "Dotation corrigée", size = 15)
	mnt_emis= fields.Integer(string = "Titre émis", size = 15)
	taux = fields.Float(string = "Taux d'exécution")



class BudgLiqOrd(models.Model):

	_name = "budg_liqord"
	_rec_name = "no_lo"
	_order = "id desc"
	
	name = fields.Char()
	no_grpadm = fields.Char()
	type_procedure = fields.Many2one('budg_typeprocedure',string="Type de procédure", readonly=True)
	no_eng = fields.Many2one("budg_engagement", "Engagement", required=True,domain=['|',('state', '=', 'V'),('state', '=', 'LC')])
	no_lo = fields.Char(string="N°liquidation", states={'N': [('readonly', True)], 'L': [('readonly', True)], 'V' :[('readonly', True)], 'A' :[('readonly', True)]}, readonly=True)
	no_brj_liq = fields.Integer()
	no_bord_pliq = fields.Integer()
	no_bord_liq = fields.Integer()
	no_brj_ap = fields.Integer()
	no_bord_ap = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	res_liq = fields.Integer(string="Reste à liquider",compute = "_mnt_restant", store = True)
	mnt_ord = fields.Integer(string="Montant ordonnancé")
	mnt_paye = fields.Integer(string="Montant à liquider", states={'N': [('readonly', True)], 'L': [('readonly', True)], 'V' :[('readonly', True)], 'A' :[('readonly', True)]})
	mnt_eng = fields.Integer(string="Montant engagement", readonly=True)
	
	cd_titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)

	
	nb_pjust = fields.Integer()
	typedossier = fields.Many2one("budg_typedossierbudg",default=lambda self: self.env['budg_typedossierbudg'].search([('code','=', 'LIQ')]), string = "Type de dossier",  readonly=True,)
	modereg = fields.Many2one('ref_modereglement','Mode de règlement',readonly=True)
	piecejust_line_ids = fields.One2many("budg_piece_liq",'liq_id')
	bank_id = fields.Many2one("res.bank", string = "Banque")
	agence_bank_id = fields.Char(string = "N° Agence")
	acc_number = fields.Char(string = "N° compte")
	dt_visa_cf = fields.Integer(string = "Date Visa Cf")
	dt_visa_ord = fields.Integer(string = "Date Visa Ord")
	dt_visa_ac = fields.Integer(string = "Date Visa Ac")
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date liquidation", required = True)
	fg_blocedit = fields.Char()
	dispo_engs = fields.Float()
	total_liq_engs = fields.Float()
	cpte_benef = fields.Char('compte')
	cpte_rub = fields.Char('cpte rub')
	imput_benef = fields.Char('imput')
	nb_edit = fields.Integer()
	no_bord_vbp = fields.Integer()
	
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	categorie_beneficiaire_id = fields.Many2one("ref_categoriebeneficiaire", string = "Caté de bénéf/four", readonly=True)
	cd_type_accompte = fields.Many2one("budg_typeaccompte", string="Type d'accompte", required=True)
	no_beneficiaire = fields.Char(string ="Nom du Bénéficiaire", readonly=True)
	cd_dev2 = fields.Integer()
	no_tb = fields.Integer()
	ref_mp = fields.Char('Réf. Marché', readonly=True)
	lb_obj = fields.Text(string="Objet", readonly=False)
	no_cpt_bp = fields.Char()
	cd_region = fields.Char()
	no_bulletin = fields.Integer()
	rf_mp = fields.Many2one("budg_marche")
	typ_budg_id = fields.Many2one("budg_typebudget")
	certif_id = fields.Many2one("budg_certification", "Motif de certification")
	dt_demande = fields.Date()
	fg_bq_txt = fields.Char()
	no_grpord = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	motif_rejet = fields.Char(string="Motif rejet")
	no_bord_trans_ord = fields.Integer()
	no_bord_trans_cf = fields.Integer()
	no_bord_trans_ac = fields.Integer()
	cd_acteur_ord = fields.Char()
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	state = fields.Selection([
	    ('draft', 'Brouillon'),
	    ('N', 'Nouveau'),
	    ('L', 'Liquidée'),
		('A', 'Annulée'),
		], 'Etat', default='draft', index=True,readonly=True, copy=False, track_visibility='always')
	active = fields.Boolean(default=True)
	signataire_dfc1 = fields.Many2one("budg_signataire",default=lambda self: self.env['budg_signataire'].search([('code', '=', 'DFC')]))
	etat = fields.Char(default="En cours")

	
	
	@api.depends('mnt_paye')
	def amount_to_words(self):
		self.text_amount = num2words(self.mnt_paye, lang='fr')
	#@api.multi
	#def action_liquidation_draft(self):
	#	self.write({'state': 'draft'})
		
	@api.multi
	def action_liquidation_confirmer(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
				
		self.env.cr.execute("select noliq from budg_compteur_liq where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
		lo = self.env.cr.fetchone()
		no_lo = lo and lo[0] or 0
		c1 = int(no_lo) + 1
		c = str(no_lo)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_lo = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_liq(x_exercice_id,company_id,noliq)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))	
		else:
			c1 = int(no_lo) + 1
			c = str(no_lo)
			ok = str(c1).zfill(4)
			self.no_lo = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_liq SET noliq = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))
		
		self.write({'state': 'N'})
       

	def afficher_piece(self):
        
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id )
		categorie = int(self.categorie_beneficiaire_id)
		val_proc = int(self.type_procedure)
		val_doc = int(self.typedossier)
		titre = int(self.cd_titre_id)
		section = int(self.cd_section_id)
		chapitre = int(self.cd_chapitre_id)
		article = int(self.cd_article_id)
		paragraphe = int(self.cd_paragraphe_id)
		eng = int(self.no_eng)

		for vals in self:
		    vals.env.cr.execute("""select b.lb_long as lib, b.oblige as obl, b.nombre as nbr, dte as dt, ref as ref from budg_piece_engagement b where b.x_exercice_id = %d and b.company_id = %d
			and b.eng_id = %d order by b.id""" %(val_ex, val_struct, eng))
		    rows = vals.env.cr.dictfetchall()
		    result = []
		    
		    vals.piecejust_line_ids.unlink()
		    for line in rows:
		        result.append((0,0, {'lb_long' : line['lib'], 'oblige': line['obl'], 'nombre': line['nbr'],  'ref': line['ref'], 'dte': line['dt']}))
		    self.piecejust_line_ids = result
	
	
	@api.multi
	def action_liquidation_liquider(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_eng = self.no_eng.no_eng
		mnt_paye = int(self.mnt_paye)
        
		if self.cd_type_accompte.cd_type_accompte == "AU":
			self.env.cr.execute("UPDATE budg_engagement SET state = 'L', reste = mnt_eng - %s WHERE no_eng = %s and x_exercice_id = %s and company_id = %s" ,(mnt_paye, val_eng, val_ex, val_struct))
		
			self.write({'state': 'L'})
			self.dispo_eng()
			self.total_liq_eng()
		else:
			self.env.cr.execute("UPDATE budg_engagement SET state = 'LC', reste = mnt_eng - %s WHERE no_eng = %s and x_exercice_id = %s and company_id = %s" ,(mnt_paye, val_eng, val_ex, val_struct))
			
			self.write({'state': 'L'})
			self.dispo_eng()
			self.total_liq_eng()

	@api.multi
	def action_liquidation_certifier(self):
		self.write({'state': 'V'})
		
	@api.multi
	def action_liquidation_annuler(self):
		self.write({'state': 'A'})
	
	@api.onchange('cd_type_accompte')
	def compute_mnt_paye(self):
		if self.cd_type_accompte.cd_type_accompte != "AU":
			self.mnt_paye = 0
			#self.no_eng.active = False
		else:
			self.mnt_paye = self.mnt_eng
		
	@api.depends('mnt_eng','mnt_paye')
	def _mnt_restant(self):
		for x in self:
			x.res_liq = x.mnt_eng - x.mnt_paye
		

	@api.onchange('no_eng')
	def no_eng_on_change(self):

		if self.no_eng:
			self.cd_titre_id = self.no_eng.cd_titre_id
			self.cd_section_id = self.no_eng.cd_section_id
			self.cd_chapitre_id = self.no_eng.cd_chapitre_id
			self.cd_article_id = self.no_eng.cd_article_id
			self.cd_paragraphe_id = self.no_eng.cd_paragraphe_id
			self.cd_rubrique_id = self.no_eng.cd_rubrique_id
			self.mnt_eng = self.no_eng.mnt_eng
			self.res_liq = self.no_eng.reste
			self.type_procedure = self.no_eng.type_procedure
			self.categorie_beneficiaire_id = self.no_eng.categorie_beneficiaire_id
			self.type_beneficiaire_id = self.no_eng.type_beneficiaire_id
			self.no_beneficiaire = self.no_eng.no_beneficiaire.nm
			self.lb_obj = self.no_eng.lb_obj
			self.cpte_benef = self.no_eng.cpte_benef
			self.cpte_rub = self.no_eng.cpte_rub
			self.imput_benef = self.no_eng.imput_benef
			self.ref_mp = self.no_eng.ref_mp
			self.modereg = self.no_eng.modereg.id

			
	

	def dispo_eng(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		v_eng = self.no_eng
	
		self.env.cr.execute("""select (sum(l.mnt_eng) - l.mnt_paye) FROM budg_liqord l, budg_engagement e
		WHERE e.id = %d and e.id = l.no_eng and l.company_id = %d and l.x_exercice_id = %d group by l.mnt_eng, l.mnt_paye""" %(v_eng, val_struct, val_ex))
		res = self.env.cr.fetchone()
		self.dispo_engs = res and res[0] or 0
	
	
	def total_liq_eng(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		v_eng = int(self.no_eng)
	
		self.env.cr.execute("""select sum(l.mnt_paye) FROM budg_liqord l, budg_engagement e
		WHERE e.id = l.no_eng and l.no_eng = %d and l.company_id = %d and l.x_exercice_id = %d group by l.mnt_paye""" %(v_eng, val_struct, val_ex))
		res = self.env.cr.fetchone()
		self.total_liq_engs = res and res[0] or 0		
	

	
class Budg_Compteur_liq(models.Model):
	
	_name = "budg_compteur_liq"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	noliq = fields.Integer()


class BudgMandat(models.Model):

	_name = "budg_mandat"
	_rec_name = "no_mandat"
	_order = "id desc"

	name = fields.Char()
	no_grpadm = fields.Char()
	cd_titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one('budg_typeprocedure',string="Type de procédure", readonly= True)
	no_eng = fields.Char(string="N° engagement", readonly= True)
	no_mandat = fields.Char(string="N° Mandat",readonly=True, states={'N': [('readonly', True)], 'O': [('readonly', True)], 'V': [('readonly', True)],'I': [('readonly', True)], 'W': [('readonly', True)]})
	no_lo = fields.Many2one("budg_liqord", string="Liquidation",domain=[('state', '=', 'L'),('etat','=','En cours')], states={'N': [('readonly', True)], 'O': [('readonly', True)], 'V': [('readonly', True)], 'I': [('readonly', True)],'W': [('readonly', True)]}, required=True)
	mnt_eng = fields.Integer(string="Montant eng.", readonly= True)
	typedossier = fields.Many2one("budg_typedossierbudg",default=lambda self: self.env['budg_typedossierbudg'].search([('code','=', 'LIQ')]), string = "Type de dossier",  readonly=True,)
	no_brj_pliq = fields.Integer()
	no_brj_liq = fields.Integer()
	no_bord_pliq = fields.Integer()
	no_bord_liq = fields.Integer()
	no_brj_ap = fields.Integer()
	no_bord_ap = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	cpte_benef = fields.Char('compte')
	cpte_rub = fields.Char('compte rub')
	imput_benef = fields.Char('imput')
	mnt_annule = fields.Integer( default=0)
	solde = fields.Integer()
	mnt_ord = fields.Integer(string="Montant", readonly=True)
	mnt_paye = fields.Integer(string="Montant payé")
	nb_pjust = fields.Integer
    #banque = fields.Many2one("res.bank", string='Banque')
	agence_id = fields.Many2one("ref_banque_agence",string="Banque")
	num_compte = fields.Char(string="N° Compte")
	piecejust_ids = fields.One2many("budg_piece_ord",'mandat_id')
	bank_id = fields.Many2one("res.bank", string = "Banque")
	agence_bank_id = fields.Char(string = "N° Agence")
	acc_number = fields.Many2one("res.partner.bank", string = "N° compte")
	dt_visa_cf = fields.Integer(string = "Date Visa Cf")
	dt_visa_ord = fields.Integer(string = "Date Visa Ord")
	dt_visa_ac = fields.Integer(string = "Date Visa Ac")
	et_doss = fields.Char()
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date mandat", required = True)
	fg_blocedit = fields.Char()
	nb_edit = fields.Integer()
	no_bord_vbp = fields.Integer()
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	categorie_beneficiaire_id = fields.Many2one("ref_categoriebeneficiaire", string = "Caté de bénéf/four", readonly=True)	
	no_beneficiaire = fields.Char( string ="Identité", readonly= True)
	cd_dev2 = fields.Integer()
	no_tb = fields.Integer()
	lb_obj = fields.Text(string="Objet mandat", readonly= True)
	obj = fields.Text(string="Objet", readonly= False)
	no_cpt_bp = fields.Char()
	ref_mp = fields.Char('Ref. Marché', readonly=True)
	modereg = fields.Many2one("ref_modereglement", 'Mode de règlement', readonly=True)
	cd_region = fields.Char()
	no_bulletin = fields.Integer()
	type_accompte_id = fields.Char(string="Type d'accompte", readonly= True)
	#type_depense_id = fields.Char(string = "Type de dépense", readonly= True)
	#cd_nature_depense = fields.Char(string ="Nature de dépense", readonly= True)
	rf_mp = fields.Many2one("budg_marche")
	typ_budg_id = fields.Many2one("budg_typebudget")
	certif_id = fields.Many2one("budg_certification")
	dt_demande = fields.Date()
	fg_bq_txt = fields.Char()
	no_grpord = fields.Integer()
	motif_rejet = fields.Char(string="Motif rejet")
	typ_pjust_id = fields.Many2one("budg_piecejustificative")
	ref_pjust = fields.Char(string="Ref.P justificative")
	no_bord_trans_ord = fields.Integer()
	no_bord_trans_cf = fields.Integer()
	no_bord_trans_ac = fields.Integer()
	cd_acteur_ord = fields.Char()
	no_lecr = fields.Integer()
	no_bord_mdt = fields.Integer()
	no_cpt_deb = fields.Integer()
	no_scpt_deb = fields.Integer()
	no_cpt_cred = fields.Integer()
	no_scpt_cred = fields.Integer()
	x_exercice_id_lecr = fields.Integer()
	no_lecr_cred = fields.Integer()
	no_lecr_pc_cred = fields.Integer()
	no_lecr_pc_deb = fields.Integer()
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	state = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Nouveau'),
		('A', 'Annulé'),
		('O', 'Ordonnancé'),
		#('V', 'Visé par DCMEF/CG'),
		#('R', 'Rejété par DCMEF/CG'),
		#('I', 'Visé par DFC/AC'),
		#('J', 'Rejété par DFC/AC'),
		('E', 'Pris en charge'),
		('F', 'Payé'),
        ], 'Etat', default='draft', index=True, readonly=True, copy=False, track_visibility='always')
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	active = fields.Boolean(default="False")
	envoyer_daf = fields.Selection([('Y','Oui'),('N','Non')], default='N')
	signataire_dfc = fields.Many2one("budg_signataire",default=lambda self: self.env['budg_signataire'].search([('code', '=', 'DFC')]))
	signataire_dg = fields.Many2one("budg_signataire",default=lambda self: self.env['budg_signataire'].search([('code', '=', 'DG')]))

	
	
	@api.depends('mnt_ord')
	def amount_to_words(self):
		self.text_amount = num2words(self.mnt_ord, lang='fr')
	
	
	@api.multi
	def action_mandat_brouillon(self):
		self.write({'state': 'draft'})
		
	@api.multi	
	def action_mandat_confirme(self):
		
		val_ex = int(self.x_exercice_id)
		v_id = int(self.no_lo.no_eng.id)
		val_struct = int(self.company_id)
		val_lo = int(self.no_lo)
		
		self.env.cr.execute("select nomand from budg_compteur_mand where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
		mandat = self.env.cr.fetchone()
		no_mandat = mandat and mandat[0] or 0
		c1 = int(no_mandat) + 1
		c = str(no_mandat)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_mandat = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_mand(x_exercice_id,company_id,nomand)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))	
		else:
			c1 = int(no_mandat) + 1
			c = str(no_mandat)
			ok = str(c1).zfill(4)
			self.no_mandat = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_mand SET nomand = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))

		self.write({'state': 'N'})
        
		self.env.cr.execute("UPDATE budg_liqord set etat = 'Terminé' where id = %d and x_exercice_id = %d and company_id = %d" %(val_lo, val_ex, val_struct))

        
       
	@api.multi
	def action_mandat_ordonnance(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_eng = str(self.no_lo.no_eng.no_eng)
		val_lo = self.no_lo.no_lo
		
		val_titre = int(self.no_lo.no_eng.cd_titre_id)
		val_chap = int(self.no_lo.no_eng.cd_chapitre_id)
		val_sec = int(self.no_lo.no_eng.cd_section_id)
		val_art = int(self.no_lo.no_eng.cd_article_id)
		val_par = int(self.no_lo.no_eng.cd_paragraphe_id)
		val_rub = int(self.no_lo.no_eng.cd_rubrique_id)

		#self.env.cr.execute("UPDATE budg_engagement SET state = 'O' WHERE no_eng = '%s' and x_exercice_id = %d and company_id = %d" %(val_eng, val_ex, val_struct))


		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET mnt_mandate = (select sum(BM.mnt_ord) 
		FROM budg_ligne_exe_dep BE, budg_engagement E, budg_mandat BM WHERE E.no_eng = BM.no_eng AND BE.cd_titre_id = E.cd_titre_id 
		and BE.cd_section_id = E.cd_section_id and BE.cd_chapitre_id = E.cd_chapitre_id and BE.cd_art_id = E.cd_article_id and
		BE.cd_paragraphe_id = E.cd_paragraphe_id and BE.cd_rubrique_id = E.cd_rubrique_id and
		BE.cd_titre_id = %d and BE.cd_section_id = %d and BE.cd_chapitre_id = %d and BE.cd_art_id = %d and BE.cd_paragraphe_id = %d and 
		BE.cd_rubrique_id = %d and BE.x_exercice_id = %d and BE.company_id = %d) WHERE cd_titre_id = %d and 
		cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d and 
		cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d""" %(val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct,val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct))
	

		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET reste_mandat = (mnt_corrige - mnt_mandate) 
		WHERE cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d 
		and cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d""" %(val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct))
	
	
		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET taux = ((mnt_mandate * 100) / mnt_corrige)
		WHERE cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d 
		and cd_paragraphe_id = %d and cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d""" %(val_titre, val_sec, val_chap, val_art, val_par,val_rub, val_ex,val_struct))
	
		
		self.write({'state': 'O'})
	
	
	def afficher_piece(self):
        
		val_liq = int(self.no_lo)


		for vals in self:
		    vals.env.cr.execute("""select b.lb_long as lib, b.oblige as obl, montant as mnt,  b.nombre as nbr, b.ref as ref, b.dte as dt 
		    from budg_piece_liq b where liq_id = %d order by b.id""" %(val_liq))
		    rows = vals.env.cr.dictfetchall()
		    result = []
		    
		    vals.piecejust_ids.unlink()
		    for line in rows:
		        result.append((0,0, {'lb_long' : line['lib'], 'oblige': line['obl'], 'nombre': line['nbr'],'montant': line['mnt'],'ref': line['ref'],'dte': line['dt']}))
		    self.piecejust_ids = result
		
	@api.multi
	def action_mandat_viser(self):
		self.write({'state': 'V'})
		
	@api.multi
	def action_mandat_pc(self):
		val_eng = self.no_lo.no_eng.no_eng
		val_t = self.no_lo.no_eng.cd_titre_id.id
		val_s = self.no_lo.no_eng.cd_section_id.id
		val_c = self.no_lo.no_eng.cd_chapitre_id.id
		val_a = self.no_lo.no_eng.cd_article_id.id
		val_p = self.no_lo.no_eng.cd_paragraphe_id.id
		val_r = self.no_lo.no_eng.cd_rubrique_id.id 
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		mnt = self.mnt_ord
		self.write({'state': 'E'})
		
		#self.env.cr.execute("UPDATE budg_engagement set state = 'P' where no_eng = '%s' and x_exercice_id = %d and company_id = %d" %(val_eng, val_ex, val_struct))

		
	#Annulation de l'engagement
	@api.multi
	def action_mandat_annule(self):
		
		val_ex = str(self.x_exercice_id)
		val_struct = str(self.company_id)
		
		self.write({'state': 'A'})
		
		self.mnt_annule = self.mnt_ord
	
	#Remise de la liquidation à l'état 'L'
		#self.env.cr.execute("UPDATE budg_liqord set state = 'L' where no_lo = '%s' and x_exercice_id = %d and company_id = %d" %(val_lo, val_ex, val_struct))

	@api.multi
	def action_mandat_visa_ac(self):
		self.write({'state': 'I'})
		
	@api.multi
	def action_mandat_rejeter_ac(self):
		self.write({'state': 'J'})
	
	"""
	@api.onchange('no_lo')
	def _action_nolo(self):
		
		if self.no_lo.state != 'V':
			self.no_lo = ""
	"""
	
		
	#Chargement de la liquidation choisie
	@api.onchange('no_lo')
	def no_lo_on_change(self):

		if self.no_lo:
			self.type_accompte_id = self.no_lo.cd_type_accompte.lb_long
			self.mnt_eng = self.no_lo.mnt_eng
			self.mnt_ord = self.no_lo.mnt_paye
			self.no_eng = self.no_lo.no_eng.no_eng
			self.obj = self.no_lo.lb_obj
			self.type_procedure = self.no_lo.type_procedure
			self.cd_titre_id = self.no_lo.cd_titre_id
			self.cd_section_id = self.no_lo.cd_section_id
			self.cd_chapitre_id = self.no_lo.cd_chapitre_id
			self.cd_article_id = self.no_lo.cd_article_id
			self.cd_paragraphe_id = self.no_lo.cd_paragraphe_id
			self.cd_rubrique_id = self.no_lo.cd_rubrique_id
			self.categorie_beneficiaire_id = self.no_lo.categorie_beneficiaire_id
			self.type_beneficiaire_id = self.no_lo.type_beneficiaire_id
			self.no_beneficiaire = self.no_lo.no_beneficiaire
			self.cpte_benef = self.no_lo.cpte_benef
			self.cpte_rub = self.no_lo.cpte_rub
			self.imput_benef = self.no_lo.imput_benef
			self.ref_mp = self.no_lo.ref_mp
			self.modereg = self.no_lo.modereg

			
	
	
class Budg_Compteur_mand(models.Model):
	
	_name = "budg_compteur_mand"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	nomand = fields.Integer(default = 0)
	
	
class BudgBordEng(models.Model):

	_name = "budg_bordereau_engagement"
	_rec_name = "no_bord_en"

	name = fields.Char()
	no_bord_eng = fields.Char(string='N° Bord. Eng',default=lambda self: self.env['ir.sequence'].next_by_code('no_bord_eng'))
	no_bord_en = fields.Char(string='Bord. N°', readonly=True)
	type_bord_trsm = fields.Char("Type de bordereau",default ="Bordereau de Transmission d'engagement pour DCMEF/CG",  readonly=True)
	cd_acteur = fields.Char(string ="Acteur", default='DAF/DFC', readonly=True)
	date_emis = fields.Date("Date émision", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date()
	num_accuse = fields.Char()
	totaux = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	cd_acteur_accuse = fields.Char(string ="Acteur")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	engagement_ids = fields.Many2many("budg_engagement", "eng_id", string="Liste des engagements", ondelete="restrict")
	state = fields.Selection([
        ('N', 'Nouveau'),
		('T', 'Envoyé à DCMEF/CG'),
		('R', 'Réceptionné par DCMEF/CG'),
        ], 'Etat', default='N', required=True, readonly=True)
	total_prec = fields.Integer()
	
	
	
	@api.depends('totaux')
	def amount_to_words(self):
		self.text_amount = num2words(self.totaux, lang='fr')
	

	@api.multi
	def action_generer_bord_eng(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_id = int(self.id)
		
			
		self.env.cr.execute("select bordeng from budg_compteur_bord_eng where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
		bordeng = self.env.cr.fetchone()
		no_bord_en = bordeng and bordeng[0] or 0
		c1 = int(no_bord_en) + 1
		c = str(no_bord_en)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_bord_eng(x_exercice_id,company_id,bordeng)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))	
		else:
			c1 = int(no_bord_en) + 1
			c = str(no_bord_en)
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_bord_eng SET bordeng = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))
	
		"""
		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '01' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '01' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '01' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0
		"""

		
		
		self.env.cr.execute(""" SELECT sum(mnt_eng) FROM budg_engagement e , budg_bordereau_engagement b, eng_id be
		WHERE b.x_exercice_id = %d AND b.company_id = %d AND be.budg_bordereau_engagement_id = %d 
		AND e.id = be.budg_engagement_id AND be.budg_bordereau_engagement_id = b.id""" %(val_ex,val_struct, val_id))
		res = self.env.cr.fetchone()
		self.totaux = res and res[0] or 0
		
		self.env.cr.execute(""" SELECT sum(totaux) FROM budg_bordereau_engagement b	
		WHERE b.x_exercice_id = %d AND b.company_id = %d and b.id != %d """ %(val_ex,val_struct, val_id))
		res1 = self.env.cr.fetchone()
		self.total_prec = res1 and res1[0] or 0
		
		self.write({'state': 'T'})
		
	"""
	@api.multi
	def action_receptionner_bord_engcf(self):
		self.write({'state': 'R'})
		self.date_recus = date.today()
	
	@api.multi
	def action_misebordereau_bord_eng(self):
		self.write({'state': 'V'})
		
		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '02' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '02' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '02' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0
		
	@api.multi
	def action_receptionner_bord_engdaf(self):
		self.write({'state': 'RD'})
	"""
		
		
	
class Budg_Compteur_bord_eng(models.Model):
	
	_name = "budg_compteur_bord_eng"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordeng = fields.Integer(default = 0)
	

class Budg_Compteur_bord_titre(models.Model):
	
	_name = "budg_compteur_bord_titre"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordtitre = fields.Integer(default = 0)
	

class BudgBordLiq(models.Model):

	_name = "budg_bordereau_liquidation"
	_rec_name="no_bord_liq1"

	no_lo = fields.Many2one("budg_bordereau_liquidation")
	no_bord_liq1 = fields.Char("Bord. N°", readonly=True)
	no_bord_liq = fields.Char(string='N° Bord. Liq',default=lambda self: self.env['ir.sequence'].next_by_code('no_bord_liq'))
	type_bord_trsm = fields.Char("Type de bordereau", readonly=True)
	cd_acteur = fields.Char(string ="Acteur", readonly=True)
	date_emis = fields.Date("Date d'émission", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception", readonly=True)
	num_accuse = fields.Char()
	totaux = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	cd_acteur_accuse = fields.Char(string ="Acteur")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	liquidation_ids = fields.Many2many("budg_liqord", "budg_detail_bord_liq", string="Liste des liquidations")
	state = fields.Selection([
        ('N', 'Nouveau'),
        ('V', 'Transmis'),
		('R', 'Receptionner'),
        ], 'Etat', default='N', index=True, required=True, readonly=True, copy=False, track_visibility='always')

	@api.depends('totaux')
	def amount_to_words(self):
		self.text_amount = num2words(self.totaux, lang='fr')


	@api.multi
	def action_misebordereau_bord_liq(self):
		
		val_ex = int(self.x_exercice_id.id)
		val_struct = int(self.company_id.id)
		val_id = self.id
		
		self.env.cr.execute("select bordliq from budg_compteur_bord_liq where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
		bordliq = self.env.cr.fetchone()
		no_bord_liq1 = bordliq and bordliq[0] or 0
		c1 = int(no_bord_liq1) + 1
		c = str(no_bord_liq1)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_bord_liq1 = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_bord_liq(x_exercice_id,company_id,bordliq)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))
		else:
			c1 = int(no_bord_liq1) + 1
			c = str(no_bord_liq1)
			ok = str(c1).zfill(4)
			self.no_bord_liq1 = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_bord_liq SET bordliq = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))
			
		self.write({'state': 'V'})
		
		
		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '03' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '03' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '03' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0
		
		
		self.env.cr.execute(""" SELECT sum(mnt_paye) FROM budg_liqord l , budg_bordereau_liquidation b, budg_detail_bord_liq bl
		WHERE b.x_exercice_id = %s AND b.company_id = %s AND bl.budg_bordereau_liquidation_id = %s
		AND l.id = bl.budg_liqord_id AND bl.budg_bordereau_liquidation_id = b.id""" %(val_ex,val_struct, val_id))
		res = self.env.cr.fetchone()
		self.totaux = res and res[0]
		print('montant')

		
	@api.multi
	def action_receptionbordereau_bord_liq(self):
		self.write({'state': 'R'})
		self.date_recus = date.today()
		
		
		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '04' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '04' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '04' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0
		
	
class Budg_Compteur_bord_liq(models.Model):
	
	_name = "budg_compteur_bord_liq"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordliq = fields.Integer(default = 0)


class BudgBordMan(models.Model):

	_name = "budg_bordereau_mandatement"
	_rec_name = "no_bord_mandat"

	name = fields.Char()
	no_bord_mandat = fields.Char("Bord. N°", readonly=True)
	type_bord_trsm = fields.Char('Type de bordereau',default='Bordereau de Transmission de Mandat pour DCMEF/CG',readonly=True)
	cd_acteur = fields.Char(string ="De",default="DAF/DFC", readonly=True)
	date_emis = fields.Date(string="Date d'émission",default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception", readonly=True)
	num_accuse = fields.Char()
	totaux = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	cd_acteur_accuse = fields.Char(string ="Vers ",default="DCMEF/CG", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	mandat_ids = fields.Many2many("budg_mandat", "budg_detail_bord_mandat", string="Liste des mandats")
	et_doss = fields.Selection([
        ('N', 'Nouveau'),
        ('V', 'Envoyé à DCMEF/CG'),
        ('R', 'Réceptionné par DCMEF/CG')
        ], 'Etat', default='N', required=True, readonly=True)
	total_prec = fields.Integer()
	
	
	@api.depends('totaux')
	def amount_to_words(self):
		self.text_amount = num2words(self.totaux, lang='fr')

	#Fonction pour générer le numero du bordereau, calculer le montant du precedent et present bordereau et affecter les acteurs et type de bordreau
	@api.multi
	def action_genererbordereau_bord_mandat(self):
		for vals in self:
			val_ex = int(vals.x_exercice_id.id)
			val_struct = int(vals.company_id.id)
			val_id = int(self.id)

			self.env.cr.execute("select bordmand from budg_compteur_bord_mand where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
			bordmand = self.env.cr.fetchone()
			no_bord_mandat = bordmand and bordmand[0] or 0
			c1 = int(no_bord_mandat) + 1
			c = str(no_bord_mandat)
			print("la val eng",type(bordmand))
			if c == "0":
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("""INSERT INTO budg_compteur_bord_mand(x_exercice_id,company_id,bordmand)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))
			else:
				c1 = int(no_bord_mandat) + 1
				c = str(no_bord_mandat)
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("UPDATE budg_compteur_bord_mand SET bordmand = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))

			"""
			self.env.cr.execute("select lb_long from budg_typebordtrans where code = '05' ")
			val = self.env.cr.fetchone()
			self.type_bord_trsm = val and val[0] or 0

			self.env.cr.execute("select type_depart from budg_typebordtrans where code = '05' ")
			val1 = self.env.cr.fetchone()
			self.cd_acteur = val1 and val1[0] or 0

			self.env.cr.execute("select type_dest from budg_typebordtrans where code = '05' ")
			val2 = self.env.cr.fetchone()
			self.cd_acteur_accuse = val2 and val2[0] or 0
			"""
			self.write({'et_doss': 'V'})


			self.env.cr.execute("""SELECT sum(mnt_ord) FROM budg_mandat m, budg_bordereau_mandatement b, budg_detail_bord_mandat bm
			WHERE b.x_exercice_id = %d AND b.company_id = %d AND bm.budg_bordereau_mandatement_id = %d
			AND m.id = bm.budg_mandat_id AND bm.budg_bordereau_mandatement_id = b.id""" %(val_ex,val_struct, val_id))
			res = self.env.cr.fetchone()
			self.totaux = res and res[0] or 0

			self.env.cr.execute("""SELECT sum(totaux) FROM budg_bordereau_mandatement b
			WHERE b.x_exercice_id = %d AND b.company_id = %d AND b.id != %d""" %(val_ex,val_struct, val_id))
			res1 = self.env.cr.fetchone()
			self.total_prec = res1 and res1[0] or 0
	
	#Fonction pour mettre le bordereau à l'etat R pour reception DAF/DFC
	"""
	@api.multi
	def action_receptionbordereau_bord_mandat(self):
		self.write({'et_doss': 'R'})
		self.date_recus = date.today()

	#Fonction pour mettre le bordereau à l'etat ER pour reception DAF/DFC
	@api.multi
	def action_misebordereau_bord_mandatdaf(self):
		self.write({'et_doss': 'ED'})
		
		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '06' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '06' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '06' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0

	# Fonction pour mettre le bordereau à l'etat RD pour reception controle
	@api.multi
	def action_receptionner_bord_mandatdaf(self):
		self.write({'et_doss': 'RD'})

	# Fonction pour mettre le bordereau à l'etat T pour envoi prise en charge
	@api.multi
	def action_envoyer_bord_mandatdpc(self):
		self.write({'et_doss': 'T'})
		
		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '07' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '07' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '07' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0
		
	@api.multi
	def action_receptionner_bord_mandatdpc(self):
		self.write({'et_doss': 'PC'})
	"""

class Budg_Compteur_bord_mand(models.Model):
	
	_name = "budg_compteur_bord_mand"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordmand = fields.Integer(default = 0)
			

class Ordre_Paiement(models.Model):
	
	_name = "budg_op"
	_rec_name = "no_op"
	
	name = fields.Char()
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	no_grpadm = fields.Char(size=4)
	no_op = fields.Char(string = "OP N°", readonly=True)
	cd_titre_id = fields.Many2one('budg_titre',string="Titre")
	cd_section_id = fields.Many2one('budg_section',string="Section")
	cd_chapitre_id = fields.Many2one('budg_chapitre',string="Chapitre")
	cd_article_id = fields.Many2one('budg_param_article',string="Article")
	cd_paragraphe_id = fields.Many2one('budg_paragraphe',string="Paragraphe")
	cd_rubrique_id = fields.Many2one('budg_rubrique',string="Rubrique")
	type_engagement_id = fields.Char(string="Type engagement")
	no_eng = fields.Many2one("budg_engagement",string="N° engagement")
	x_exercice_id_mandat = fields.Char()
	no_mandat = fields.Many2one("budg_mandat",string="N° Mandat")
	type_operation = fields.Many2one("budg_typeordrepaiement", string="Type OP", required=True)
	#type_depense = fields.Many2one("budg_typedepense", string = "Type de dépense", required=True)
	#nature_depense = fields.Many2one("budg_naturedepense", string = "Nature de dépense", required=True)
	no_cpt_tiers = fields.Many2one("compta_plan_line",string="Compte de tiers", required=False)
	ty_dest = fields.Char(size = 1)
	id_dest = fields.Char(size = 10)
	date_emis = fields.Date(string="Date OP",default=fields.Date.context_today, readonly=True)
	date_etat = fields.Date()
	mnt_op =fields.Float("Montant", required=True)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	md_reglement = fields.Many2one("ref_modereglement", string="Mode de paiement")
	lb_obj = fields.Text("Objet", size=350, required=True)
	mnt_paye = fields.Integer(size = 15)
	cd_certif = fields.Many2one("budg_certification", string="Motif certification")
	type_beneficiaire = fields.Many2one("ref_typebeneficiaire", string="Catégorie de bénéficiaire")
	no_beneficiaire = fields.Many2one("ref_beneficiaire", string="Bénéficiaire")
	x_exercice_id_lecr = fields.Integer(size=4)
	no_lecr_cred = fields.Integer(size=8)
	motif_rejet = fields.Text("Motif de rejet", size=240)
	piece_ids = fields.Many2one("budg_typepjbudget","Pièce Just.")
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	et_doss = fields.Selection([
        ('draft', 'Brouillon'),
        ('N', 'Confirmer'),
        ('C', 'Certifier'),
		('F', 'Payé'),
        ], 'Etat', default='draft', required=True, readonly=True, copy=False, track_visibility='always')
	
	@api.depends('mnt_op')
	def amount_to_words(self):
		self.text_amount = num2words(self.mnt_op, lang='fr')
	
	@api.multi
	def action_op_draft(self):
		self.write({'et_doss': 'draft'})

	@api.multi
	def action_op_confirmer(self):
		for vals in self:
			val_ex = int(vals.x_exercice_id.id)
			val_struct = int(vals.company_id.id)

			vals.env.cr.execute("select op from budg_compteur_ordre_paiement where x_exercice_id = %d and company_id = %d" %(val_ex,val_struct) )
			ope = self.env.cr.fetchone()
			no_op = ope and ope[0] or 0
			c1 = int(no_op) + 1
			c = str(no_op)
			#print("la val eng",type(ope))
			if c == "0":
				ok = str(c1).zfill(4)
				self.no_op = ok
				vals = c1
				self.env.cr.execute("""INSERT INTO budg_compteur_ordre_paiement(x_exercice_id,company_id,op)  VALUES(%d, %d, %d)""" %(val_ex,val_struct,vals))
			else:
				c1 = int(no_op) + 1
				c = str(no_op)
				ok = str(c1).zfill(4)
				self.no_op = ok
				vals = c1
				self.env.cr.execute("UPDATE budg_compteur_ordre_paiement SET op = %d  WHERE x_exercice_id = %d and company_id = %d" %(vals,val_ex,val_struct))

			self.write({'et_doss': 'N'})
		
	@api.multi
	def action_op_certifier(self):
		self.write({'et_doss': 'C'})
	
class Budg_compteur_ordre_paiement(models.Model):
	
	_name = "budg_compteur_ordre_paiement"
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	op = fields.Integer(default = 0)	
	

class Budg_Balance(models.Model):
	@api.depends('type','dt_debut', 'dt_fin')
	def _concate(self):
		for test in self:
			test.concate = "BALANCE DES" + " " + " " + str(test.type)+ " " + "DU" + " " +str(test.dt_debut)+ " " + "AU" + " " +str(test.dt_fin)
		
	_name = 'budg_balance'
	_rec_name = 'concate'
	
	concate = fields.Char(compute = '_concate')
	type = fields.Selection([
		('DEPENSES', 'Dépense'),
		('RECETTES', 'Recette')], string = "Balance",default="DEPENSES", readonly=True, required = True)
	dt_debut = fields.Date("Date début",required = True)
	dt_fin = fields.Date("Date fin", required = True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	balance_lines = fields.One2many("budg_balance_line", "balance_id")
	total_budget = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	total_engagement = fields.Integer()
	total_mandat = fields.Integer()


	@api.onchange('dt_fin')
	def change_dt_fin(self):
		
		if self.dt_fin < self.dt_debut:
			raise ValidationError(_('La date de début ne peut être supérieure à la date de fin'))
	
	
	def remplir_balance(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = self.dt_debut
		val_fin = self.dt_fin
		balance_id = self.id
		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT br.rubrique as code, br.lb_long as libelle, e.mnt_corrige as montant, en.mnt_eng as engagement, bm.mnt_ord as mandat,(bm.mnt_ord * 100)/ e.mnt_corrige as taux 
			FROM budg_ligne_exe_dep e,  budg_rubrique br, budg_engagement en, budg_mandat bm WHERE e.cd_rubrique_id = br.id AND br.id = en.cd_rubrique_id AND bm.no_eng = en.no_eng 
			AND en.company_id = %s and en.dt_etat BETWEEN '%s' and '%s' order by code asc""" ,(val_struct, val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.balance_lines.unlink()
			for line in rows:
				result.append((0,0, {'numero_compte' : line['code'], 'libelle': line['libelle'], 'montant_budgetise': line['montant'], 'montant_engagement': line['engagement'], 'montant_mandatement': line['mandat'],'taux': line['taux']}))
			self.balance_lines = result
			
	
class Budg_balance_line(models.Model):
	_name = 'budg_balance_line'
	
	balance_id = fields.Many2one("budg_balance")
	numero_compte = fields.Char("Numéro compte")
	libelle = fields.Char("Libellé")
	montant_budgetise = fields.Float("Prévisions corrigées")
	montant_engagement = fields.Float("Engagements")
	montant_mandatement = fields.Float("Mandats")
	taux = fields.Float("Taux de réalisation (%)")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)



class Budg_BalanceRecette(models.Model):
	@api.depends('type','dt_debut', 'dt_fin')
	def _concate(self):
		for test in self:
			test.concate = "BALANCE DES" + " " + " " + str(test.type)+ " " + "DU" + " " +str(test.dt_debut)+ " " + "AU" + " " +str(test.dt_fin)
		
	_name = 'budg_balance_recette'
	_rec_name = 'concate'
	
	concate = fields.Char(compute = '_concate')
	type = fields.Selection([
		('DEPENSES', 'Dépense'),
		('RECETTES', 'Recette')], string = "Balance", default= 'RECETTES',readonly=True, required = True)
	dt_debut = fields.Date("Date début",required = True)
	dt_fin = fields.Date("Date fin", required = True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	balance_lines = fields.One2many("budg_balance_line_recette", "balance_id")
	total_budget = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	total_engagement = fields.Integer()
	total_mandat = fields.Integer()


	@api.onchange('dt_fin')
	def change_dt_fin(self):
		
		if self.dt_fin < self.dt_debut:
			raise ValidationError(_('La date de début ne peut être supérieure à la date de fin'))
	
	
	def remplir_balance(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_debut)
		val_fin = str(self.dt_fin)
		balance_id = self.id
		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT p.paragraphe as code, rp.lb_long as libelle, r.mnt_budgetise as montant, re.mnt_rec as emis, (re.mnt_rec * 100)/r.mnt_budgetise as taux
			FROM budg_ligne_exe_rec r, budg_paragraphe p, budg_titrerecette re, ref_paragraphe rp 
			WHERE r.cd_paragraphe_id = p.id AND re.cd_paragraphe_id = p.id AND rp.id = p.paragraphe and r.company_id = %s and re.dt_rec BETWEEN %s and %s order by code """ ,(val_struct, val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.balance_lines.unlink()
			for line in rows:
				result.append((0,0, {'numero_compte' : line['code'], 'libelle': line['libelle'], 'montant_budgetise': line['montant'], 'montant_recette': line['emis'], 'taux': line['taux']}))
			self.balance_lines = result
		
	
class Budg_balance_line_recette(models.Model):
	_name = 'budg_balance_line_recette'
	
	balance_id = fields.Many2one("budg_balance_recette")
	numero_compte = fields.Char("Numéro compte")
	libelle = fields.Char("Libellé")
	montant_budgetise = fields.Float("Prévision initale")
	montant_recette = fields.Float("Titres émis")
	taux = fields.Float("Taux de réalisation (%)")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Budg_fiche_compte(models.Model):
	_name = 'budg_fiche_compte'
	_rec_name = 'numero_compte'
	
	numero_compte = fields.Many2one("budg_paragraphe", "N° et intitulé Compte", required=True)
	libelle = fields.Char("Libellé")
	budget_initial = fields.Float("Budget initial", readonly=True)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	ouverture = fields.Float("Ouverture", readonly=True)
	annulation = fields.Float("Annulation", readonly=True)
	budget_corrige = fields.Float("Budget corrigé", readonly=True)
	fiche_lines = fields.One2many("budg_fiche_compte_line", "fiche_id", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


	@api.onchange('numero_compte')	
	def compte(self):
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_para = int(self.numero_compte)
		
		if self.numero_compte:
			self.env.cr.execute("""select l.mnt_budgetise from budg_ligne_exe_dep l where l.cd_paragraphe_id = %s and l.x_exercice_id = %s and l.company_id = %s""" ,(val_para,val_ex,val_struct))
				
			res = self.env.cr.fetchone()
			self.budget_initial = res and res[0] or 0
			
			self.env.cr.execute("""select l.mnt_corrige from budg_ligne_exe_dep l where l.cd_paragraphe_id = %s and l.x_exercice_id = %s and l.company_id = %s""" ,(val_para,val_ex,val_struct))
				
			res1 = self.env.cr.fetchone()
			self.budget_corrige = res1 and res1[0] or 0
		
	
	def fiche_compte(self):
        
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_para = int(self.numero_compte)
    
		for vals in self:
			vals.env.cr.execute("""select e.dt_etat as dte, concat(e.no_eng, '/', bm.no_mandat) as noeng, e.lb_obj as objet, e.mnt_eng as eng, e.mnt_annule as ann1, (e.mnt_eng - e.mnt_annule) as cumul1, bm.mnt_ord as ord, bm.mnt_annule as ann2,
			(bm.mnt_ord - bm.mnt_annule) as cumul2 from budg_engagement e, budg_mandat bm, budg_liqord bl 
			where e.cd_paragraphe_id = %s and e.id = bl.no_eng and bl.id = bm.no_lo and e.x_exercice_id = %s and e.company_id = %s""",(val_para,val_ex, val_struct))
			rows = vals.env.cr.dictfetchall()
			result = []
            
			vals.fiche_lines.unlink()
			for line in rows:
			    result.append((0,0, {'date_eng' : line['dte'], 'numero_eng': line['noeng'], 'objet': line['objet'], 'montant_eng': line['eng'], 'montant_ann': line['ann1'],
				'cumul_eng': line['cumul1'],'montant_mand': line['ord'],'montant_mand_ann': line['ann2'],'cumul_mand': line['cumul2']}))
			self.fiche_lines = result
        
		for x in self.fiche_lines:
			x.cumulg = x.cumul_eng + x.cumul_mand
            

class Budg_fiche_compte_line(models.Model):
	_name = 'budg_fiche_compte_line'
	
	fiche_id = fields.Many2one('budg_fiche_compte', ondelete='cascade')
	date_eng = fields.Date("Date")
	journal = fields.Char("JNL")
	folio = fields.Char("Folio")
	numero_eng = fields.Char("N° Eng/N° Mdt")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	montant_eng = fields.Float("Emission Eng.(1)")
	montant_ann = fields.Float("Annulation Eng.(2)")
	objet = fields.Text("Objet")
	cumul_eng = fields.Float("Cumul(3=1-2)")
	montant_mand = fields.Float("Emission Mdt.(4)")
	montant_mand_ann = fields.Float("Annulation Mdt.(5)")
	cumul_mand = fields.Float("Cumul(6=4-5)")
	cumulg = fields.Float("Cumuls généraux(7=6+3)")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Budg_fiche_compteRec(models.Model):
	_name = 'budg_fiche_compte_rec'
	_rec_name = 'numero_compte'
	
	numero_compte = fields.Many2one("budg_paragraphe", "N° et intitulé Compte", required=True)
	libelle = fields.Char("Libellé")
	budget_initial = fields.Float("Budget initial", readonly=True)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	ouverture = fields.Float("Ouverture", readonly=True)
	annulation = fields.Float("Annulation", readonly=True)
	budget_corrige = fields.Float("Budget corrigé", readonly=True)
	fiche_lines = fields.One2many("budg_fiche_compte_line_rec", "fiche_id")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


	@api.onchange('numero_compte')	
	def compte(self):
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_para = int(self.numero_compte)
		
		if self.numero_compte:
			self.env.cr.execute("""select l.mnt_budgetise from budg_ligne_exe_rec l where l.cd_paragraphe_id = %s and l.x_exercice_id = %s and l.company_id = %s""" ,(val_para,val_ex,val_struct))
				
			res = self.env.cr.fetchone()
			self.budget_initial = res and res[0] or 0
		
	
	def fiche_compte_rec(self):
        
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_para = int(self.numero_compte)
    
		for vals in self:
			vals.env.cr.execute("""select bt.dt_rec as dte, bt.cd_titre_recette as titre, bt.mnt_rec as mnt, bt.mnt_annule as annule, (bt.mnt_rec - bt.mnt_annule) as cumul 
			from budg_titrerecette bt where bt.cd_paragraphe_id = %s and bt.x_exercice_id = %s and bt.company_id = %s""",(val_para,val_ex, val_struct))
			rows = vals.env.cr.dictfetchall()
			result = []
            
			vals.fiche_lines.unlink()
			for line in rows:
			    result.append((0,0, {'date_rec' : line['dte'], 'numero_titre': line['titre'], 'montant_rec': line['mnt'], 'montant_ann': line['annule'], 'cumul': line['cumul']}))
			self.fiche_lines = result
        
            

class Budg_fiche_compte_linerec(models.Model):
	_name = 'budg_fiche_compte_line_rec'
	
	fiche_id = fields.Many2one('budg_fiche_compte_rec', ondelete='cascade')
	date_rec = fields.Date("Date")
	numero_titre = fields.Char("N° Titre")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	montant_rec = fields.Float("Emission(1)")
	montant_ann = fields.Float("Annulation(2)")
	cumul = fields.Float("Cumul(3=1-2)")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Budg_synthese(models.Model):
	@api.depends('cd_rubrique_id')
	def _concatenate(self):
		for test in self:
			test.visu ="Synthèse de la rubrique"+ " " +str(test.cd_rubrique_id.concate_rubrique)
	_name = 'budg_synthese_rubrique'
	_rec_name = "visu"
	
	visu = fields.Char(compute="_concatenate")
	cd_titre_id = fields.Many2one("budg_titre",default=lambda self: self.env['budg_titre'].search([('cd_titre','=', 'II')]), string = "Titre", required=False)
	cd_section_id = fields.Many2one("budg_section", "Section", required=False)
	cd_chapitre_id = fields.Many2one("budg_chapitre", "Chapitre", required=False)
	cd_article_id = fields.Many2one("budg_param_article", "Article", required=False)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", "Paragraphe", required=False)
	cd_rubrique_id = fields.Many2one("budg_rubrique", "Rubrique", required=False)
	dt_appro_deb = fields.Date("Date debut", required=False)
	dt_appro_fin = fields.Date("Date fin", required=False)
	tout = fields.Boolean("Tous les engagements")
	etat = fields.Selection([
		('L', 'Engagement liquidé'),
		('N', 'Engagement à état nouveau'),
		('O', 'Engagement ordonnancé'),
		('V', 'Engagement approuvé'),
		('W', 'Engagement visé'),
		], 'Etat')
	rubrique_lines = fields.One2many("budg_synthese_rubrique_line", 'synthese_id', readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

	
	def remplir_synthese(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_appro_deb)
		val_fin = str(self.dt_appro_fin)
		synthese_id = self.id
		val_etat = str(self.etat)
		rub = int(self.cd_rubrique_id)

		if self.cd_rubrique_id:

			for vals in self:
				vals.env.cr.execute("""SELECT DISTINCT e.no_eng as numero, e.dt_etat as dte, e.lb_obj as objet, e.mnt_eng as montant
				FROM budg_engagement e WHERE e.cd_rubrique_id = %s AND 
				e.company_id = %s AND e.dt_etat BETWEEN %s and %s order by e.dt_etat """ ,(rub,val_struct, val_deb, val_fin))
				rows = vals.env.cr.dictfetchall()
				result = []

				vals.rubrique_lines.unlink()
				for line in rows:
					result.append((0,0, {'noeng' : line['numero'], 'dte': line['dte'],'objet': line['objet'], 'montant': line['montant']}))
				self.rubrique_lines = result

		elif self.cd_rubrique_id and self.etat:

			for vals in self:
				vals.env.cr.execute("""SELECT DISTINCT e.no_eng as numero, e.dt_etat as dte, e.lb_obj as objet, e.mnt_eng as montant
				FROM budg_engagement e WHERE e.cd_rubrique_id = %s AND e.state = %s e.x_exercice_id = %s AND e.company_id = %s order by e.dt_etat""",(rub, val_etat, val_ex, val_struct))
				rows = vals.env.cr.dictfetchall()
				result = []

				vals.rubrique_lines.unlink()
				for line in rows:
					result.append((0, 0, {'noeng': line['numero'],  'dte': line['dte'], 'objet': line['objet'], 'montant': line['montant']}))
				self.rubrique_lines = result

		elif self.tout == True:

			for vals in self:
				vals.env.cr.execute("""SELECT DISTINCT e.no_eng as numero, e.dt_etat as dte, e.lb_obj as objet, e.mnt_eng as montant
				FROM budg_engagement e WHERE e.x_exercice_id = %d AND e.company_id = %d order by e.dt_etat""" %(val_ex, val_struct))
				rows = vals.env.cr.dictfetchall()
				result = []

				vals.rubrique_lines.unlink()
				for line in rows:
					result.append((0, 0, {'noeng': line['numero'], 'dte': line['dte'], 'objet': line['objet'], 'montant': line['montant']}))
				self.rubrique_lines = result

		elif self.tout == True and self.dt_appro_deb and self.dt_appro_fin:

			for vals in self:
				vals.env.cr.execute("""SELECT DISTINCT e.no_eng as numero, e.dt_etat as dte, e.lb_obj as objet, e.mnt_eng as montant
				FROM budg_engagement e WHERE e.company_id = %s AND e.dt_etat BETWEEN %s and %s order by e.dt_etat""" ,(val_struct, val_deb, val_fin))
				rows = vals.env.cr.dictfetchall()
				result = []

				vals.rubrique_lines.unlink()
				for line in rows:
					result.append((0, 0, {'noeng': line['numero'],  'dte': line['dte'], 'objet': line['objet'], 'montant': line['montant']}))
				self.rubrique_lines = result


class Budg_synthese_line(models.Model):
	_name = 'budg_synthese_rubrique_line'
	
	synthese_id = fields.Many2one('budg_synthese_rubrique', ondelete='cascade')
	noeng = fields.Char("N° eng", readonly=True)
	objet = fields.Text("Objet", readonly=True)
	montant = fields.Integer("Montant", readonly=True)
	dte = fields.Date("Date", readonly=True)
	rubrique = fields.Many2one("budg_rubrique", "Imputation", readonly=True)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)



class Budg_synthese_liq(models.Model):
	@api.depends('cd_rubrique_id')
	def _concatenate(self):
		for test in self:
			test.visu ="Synthèse de la rubrique"+ " " +str(test.cd_rubrique_id.concate_rubrique)
	_name = 'budg_synthese_liq_rubrique'
	_rec_name = "visu"
	
	visu = fields.Char(compute="_concatenate")
	cd_titre_id = fields.Many2one("budg_titre",default=lambda self: self.env['budg_titre'].search([('cd_titre','=', 'II')]), string = "Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", "Chapitre", required=True)
	cd_article_id = fields.Many2one("budg_param_article", "Article", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", "Paragraphe", required=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", "Rubrique", required=True)
	dt_appro_deb = fields.Date("Date d'approbation", required=True)
	dt_appro_fin = fields.Date(required=True)
	etat = fields.Selection([
		('L', 'Engagement liquidé'),
		('N', 'Engagement à état nouveau'),
		('O', 'Engagement ordonnancé'),
		('R', 'Engagement rejeté'),
		('V', 'Engagement approuvé'),
		('W', 'Engagement visé'),
		], 'Etat', required=False)
	rubrique_liq_lines = fields.One2many("budg_synthese_liq_rubrique_line", 'synthese_liq_id')
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

	
	def remplir_synthese_liq(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_appro_deb)
		val_fin = str(self.dt_appro_fin)
		val_titre = int(self.cd_titre_id)
		val_section = int(self.cd_section_id)
		val_chap = int(self.cd_chapitre_id)
		val_art = int(self.cd_article_id)
		val_para = int(self.cd_paragraphe_id)
		val_rub = int(self.cd_rubrique_id)
		val_struct = int(self.company_id)
		val_etat = str(self.etat)
		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT l.no_lo as liq, l.lb_obj as objet, l.mnt_paye as montant, l.state as etat
			FROM budg_liqord l
			WHERE l.cd_titre_id = %s AND l.cd_section_id = %s AND
			l.cd_chapitre_id = %s AND l.cd_article_id = %s AND
			l.cd_paragraphe_id = %s AND l.cd_rubrique_id = %s AND 
			l.company_id = %s AND
			l.dt_etat BETWEEN %s AND %s """ ,(val_titre, val_section, val_chap, val_art, val_para, val_rub, val_struct, val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.rubrique_liq_lines.unlink()
			for line in rows:
				result.append((0,0, {'noliq': line['liq'], 'objet': line['objet'], 'montant': line['montant'], 'etat': line['etat']}))
			self.rubrique_liq_lines = result

class Budg_synthese_liq_line(models.Model):
	_name = 'budg_synthese_liq_rubrique_line'
	
	synthese_liq_id = fields.Many2one('budg_synthese_liq_rubrique', ondelete='cascade')
	noeng = fields.Char("N° eng")
	noliq = fields.Char("N° liq")
	objet = fields.Char("Objet")
	etat = fields.Char("Etat")
	montant = fields.Integer("Montant")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Budg_synthese_mdt(models.Model):
	@api.depends('cd_rubrique_id')
	def _concatenate(self):
		for test in self:
			test.visu ="Synthèse de la rubrique"+ " " +str(test.cd_rubrique_id.concate_rubrique)
	_name = 'budg_synthese_mdt_rubrique'
	_rec_name = "visu"
	
	visu = fields.Char(compute="_concatenate")
	cd_titre_id = fields.Many2one("budg_titre",default=lambda self: self.env['budg_titre'].search([('cd_titre','=', 'II')]), string = "Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", "Chapitre", required=True)
	cd_article_id = fields.Many2one("budg_param_article", "Article", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", "Paragraphe", required=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", "Rubrique", required=True)
	dt_appro_deb = fields.Date("Date d'approbation", required=True)
	dt_appro_fin = fields.Date(required=True)
	etat = fields.Selection([
		('L', 'Engagement liquidé'),
		('N', 'Engagement à état nouveau'),
		('O', 'Engagement ordonnancé'),
		('R', 'Engagement rejeté par CF/CG'),
		('V', 'Engagement approuvé par DAF'),
		('W', 'Engagement visé par CF/CG'),
		], 'Etat', required=False)
	mandat_liq_lines = fields.One2many("budg_synthese_mdt_rubrique_line", 'synthese_mdt_id', readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

	
	def remplir_mdt_liq(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_appro_deb)
		val_fin = str(self.dt_appro_fin)
		val_titre = int(self.cd_titre_id)
		val_section = int(self.cd_section_id)
		val_chap = int(self.cd_chapitre_id)
		val_art = int(self.cd_article_id)
		val_para = int(self.cd_paragraphe_id)
		val_rub = int(self.cd_rubrique_id)
		val_etat = str(self.etat)
		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT m.no_mandat as numero, m.obj as objet, m.mnt_ord as montant, m.state as etat
			FROM budg_mandat m
			WHERE m.cd_titre_id = %s AND m.cd_section_id = %s AND
			m.cd_chapitre_id = %s AND m.cd_article_id = %s AND
			m.cd_paragraphe_id = %s AND m.cd_rubrique_id = %s
			AND m.company_id = %s 
			AND m.dt_etat BETWEEN %s AND %s""" ,(val_titre, val_section, val_chap, val_art, val_para, val_rub, val_struct, val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.mandat_liq_lines.unlink()
			for line in rows:
				result.append((0,0, {'nomdt' : line['numero'], 'objet': line['objet'], 'montant': line['montant'], 'etat': line['etat']}))
			self.mandat_liq_lines = result


class Budg_synthese_mdt_line(models.Model):
	_name = 'budg_synthese_mdt_rubrique_line'
	
	synthese_mdt_id = fields.Many2one('budg_synthese_mdt_rubrique', ondelete='cascade')
	nomdt = fields.Char("N° mandat")
	objet = fields.Char("Objet")
	etat = fields.Char("Etat")
	montant = fields.Integer("Montant")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class Budg_synthese_rec(models.Model):
	@api.depends('cd_rubrique_id')
	def _concatenate(self):
		for test in self:
			test.visu ="Synthèse de la rubrique"+ " " +str(test.cd_rubrique_id.concate_rubrique)
	_name = 'budg_synthese_rec'
	_rec_name = "visu"
	
	visu = fields.Char(compute="_concatenate")
	cd_titre_id = fields.Many2one("budg_titre",default=lambda self: self.env['budg_titre'].search([('cd_titre','=', 'I')]), string = "Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", "Chapitre", required=True)
	cd_article_id = fields.Many2one("budg_param_article", "Article", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", "Paragraphe", required=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", "Rubrique", required=True)
	dt_appro_deb = fields.Date("Date d'approbation", required=True)
	dt_appro_fin = fields.Date(required=True)
	etat = fields.Selection([
		('N', 'Nouveau'),
		('V', 'Approuvé'),
		('W', 'Validé'),
		], 'Etat', required=True)
	recette_lines = fields.One2many("budg_synthese_recette_line", 'synthese_rec_id')
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

	
	def remplir_synthese_rec(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_appro_deb)
		val_fin = str(self.dt_appro_fin)
		val_titre = int(self.cd_titre_id)
		val_section = int(self.cd_section_id)
		val_chap = int(self.cd_chapitre_id)
		val_art = int(self.cd_article_id)
		val_para = int(self.cd_paragraphe_id)
		val_rub = int(self.cd_rubrique_id)
		val_struct = int(self.company_id)
		val_etat = str(self.etat)
		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT t.cd_titre_recette as numero,  t.lb_objet as objet, t.mnt_rec as montant
			FROM budg_titrerecette t
			WHERE t.cd_titre_id = %s AND t.cd_section_id = %s AND
			t.cd_chapitre_id = %s AND t.cd_article_id = %s AND
			t.cd_paragraphe_id = %s AND t.cd_rubrique_id = %s AND 
			t.company_id = %s AND t.et_doss = %s
			AND t.dt_rec BETWEEN %s AND %s """ ,(val_titre, val_section, val_chap, val_art, val_para, val_rub, val_struct, val_etat,val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.recette_lines.unlink()
			for line in rows:
				result.append((0,0, {'notitre' : line['numero'], 'objet': line['objet'], 'montant': line['montant']}))
			self.recette_lines = result

class Budg_synthese_rec_line(models.Model):
	_name = 'budg_synthese_recette_line'
	
	synthese_rec_id = fields.Many2one('budg_synthese_rec', ondelete='cascade')
	notitre = fields.Char("N° titre")
	objet = fields.Char("Objet")
	montant = fields.Float("Montant")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


	
class Budg_journal_eng(models.Model):
	@api.depends('dt_appro_deb', 'dt_appro_fin')
	def _concatenate(self):
		for test in self:
			test.visu ="JOURNAL DES ENGAGEMENTS DU" + " " +str(test.dt_appro_deb)+ " " + "AU " + " " +str(test.dt_appro_fin)
	_rec_name = "visu"
	_name = 'budg_journal_eng'
	
	visu = fields.Char(compute='_concatenate')
	dt_appro_deb = fields.Date("Date d'approbation", required=True)
	dt_appro_fin = fields.Date(required=True)
	jnl_eng_lines = fields.One2many("budg_journal_eng_line", "jnl_eng_id",)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
	
	@api.onchange('dt_appro_fin')
	def change_dt_fin(self):
		
		if self.dt_appro_fin < self.dt_appro_deb:
			raise ValidationError(_('La date de début ne peut être supérieure à la date de fin'))
	
	
	def remplir_jnl_eng(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_appro_deb)
		val_fin = str(self.dt_appro_fin)

		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT e.dt_etat as periode, b.nm as creancier,e.no_eng as eng, m.no_mandat as nomandat, e.mnt_eng as engagement, rp.cd_paragraphe as imputation, 
			m.mnt_ord as mandat, (e.mnt_eng - m.mnt_ord) as solde
			FROM budg_engagement e, budg_paragraphe p, budg_mandat m,ref_beneficiaire b, ref_paragraphe rp
			WHERE rp.id = p.paragraphe and p.id = e.cd_paragraphe_id AND e.company_id = %s AND b.id = e.no_beneficiaire
			AND e.dt_etat BETWEEN %s and %s AND e.no_eng = m.no_eng AND b.id = e.no_beneficiaire""" ,(val_struct,val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.jnl_eng_lines.unlink()
			for line in rows:
				result.append((0,0, {'date_deb' : line['periode'], 'creancier': line['creancier'], 'ref_eng': line['eng'], 'no_mandat': line['nomandat'], 'mnt_eng': line['engagement'], 'imputation': line['imputation'], 'mnt_mand': line['mandat'], 'solde': line['solde']}))
			self.jnl_eng_lines = result
		
	
	
class Budg_journal_line(models.Model):
	_name = 'budg_journal_eng_line'
	
	jnl_eng_id = fields.Many2one("budg_journal_eng", ondelete='cascade')
	date_deb = fields.Date('Date', readonly=True)
	creancier = fields.Char('Bénéficiare', readonly=True)
	ref_eng = fields.Char("Ref. eng.", readonly=True)
	no_mandat = fields.Char("N° Mandat", readonly=True)
	imputation = fields.Char("Imputation", readonly=True)
	mnt_eng = fields.Float("Engagement", readonly=True)
	mnt_deg = fields.Float("Dégagement", readonly=True)
	mnt_mand = fields.Float("Mandat", readonly=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	solde = fields.Integer("Solde", readonly=True)
	

class Budg_journal_mdt(models.Model):
	@api.depends('dt_appro_deb', 'dt_appro_fin')
	def _concatenate(self):
		for test in self:
			test.visu ="JOURNAL DES DEPENSES DU "+ " " +str(test.dt_appro_deb)+ " AU" + " "  +str(test.dt_appro_fin)
	_rec_name = "visu"
	_name = 'budg_journal_mdt'
	
	visu = fields.Char(compute='_concatenate')
	dt_appro_deb = fields.Date("Date d'approbation", required=True)
	dt_appro_fin = fields.Date(required=True)
	jnl_mdt_lines = fields.One2many("budg_journal_mdt_line", "jnl_mdt_id")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
	
	@api.onchange('dt_appro_fin')
	def change_dt_fin(self):
		
		if self.dt_appro_fin < self.dt_appro_deb:
			raise ValidationError(_('La date de début ne peut être supérieure à la date de fin'))
	
	
	def remplir_jnl_mdt(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_appro_deb)
		val_fin = str(self.dt_appro_fin)

		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT e.dt_etat as periode, b.nm as creancier, m.no_mandat as nomandat,
			rp.cd_paragraphe as imputation, m.mnt_ord as emission, m.mnt_annule as annule, m.mnt_ord - m.mnt_annule as solde
			FROM budg_engagement e, budg_paragraphe p, budg_mandat m, ref_beneficiaire b,ref_paragraphe rp
			WHERE rp.id = p.paragraphe and p.id = e.cd_paragraphe_id AND e.company_id = %s AND b.id = e.no_beneficiaire
			AND e.dt_etat BETWEEN %s and %s AND e.no_eng = m.no_eng and m.state != 'A' and m.state != 'R' """ ,(val_struct,val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.jnl_mdt_lines.unlink()
			for line in rows:
				result.append((0,0, {'date_deb' : line['periode'], 'creancier': line['creancier'], 'no_mandat': line['nomandat'], 'imputation': line['imputation'], 'mnt_emis': line['emission'], 'mnt_annule': line['annule'], 'solde': line['solde']}))
			self.jnl_mdt_lines = result
		
	
class Budg_journal_mdt_line(models.Model):
	_name = 'budg_journal_mdt_line'
	
	jnl_mdt_id = fields.Many2one("budg_journal_mdt", ondelete='cascade')
	date_deb = fields.Date('Date')
	creancier = fields.Char('Créancier')
	ref_bord = fields.Char("Ref. Bord.")
	no_mandat = fields.Char("N° Mandat")
	imputation = fields.Char("Imputation")
	mnt_emis = fields.Float("Emission")
	mnt_annule = fields.Float("Annulation")
	solde = fields.Float("Solde")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)


class Budg_journal_rec(models.Model):
	@api.depends('dt_appro_deb', 'dt_appro_fin')
	def _concatenate(self):
		for test in self:
			test.visu ="Journal des titres de recettes du" + " " +str(test.dt_appro_deb)+ "au" + " " +str(test.dt_appro_fin)
	_rec_name = "visu"
	_name = 'budg_journal_rec'
	
	visu = fields.Char(compute='_concatenate')
	dt_appro_deb = fields.Date("Date d'approbation", required=True)
	dt_appro_fin = fields.Date(required=True)
	jnl_rec_lines = fields.One2many("budg_journal_rec_line", "jnl_rec_id")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
	
class Budg_journal_rec_line(models.Model):
	_name = 'budg_journal_rec_line'
	
	jnl_rec_id = fields.Many2one("budg_journal_rec", ondelete='cascade')
	date_deb = fields.Date('Date')
	debiteur = fields.Char('Débiteur')
	no_titre = fields.Char("N° Titre")
	imputation = fields.Char("Imputation")
	mnt_emis = fields.Integer("Emission")
	mnt_annule = fields.Integer("Annulation")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	solde = fields.Integer("Solde")


class BudgBudgetAgrege(models.Model):
    _name = 'budg_budget_agrege'
    _rec_name = 'budget_id'
    
    budget_id = fields.Many2one('budg_budget', 'Budget', required=True)
    budg_budget_agrege_ids = fields.One2many('budg_budget_agrege_line','budget_id')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
    
    
    def rechercher(self):
        
        val_ex = int(self.x_exercice_id)
        val_struct = int(self.company_id)
        val_b = int(self.budget_id)
        

        for vals in self:
            vals.env.cr.execute("""SELECT rt.cd_titre as titre, rs.cd_section as section, rc.cd_chapitre as chapitre,  
			ra.cd_article as article, rp.cd_paragraphe as para, rp.lb_long as nature, sum(bl.mnts_ant1) as mnt1, sum(bl.mnts_ant1exe) as mnt11, sum(bl.mnts_ant2) as mnt2, sum(bl.mnts_ant2exe) as mnt22,
			sum(bl.mnts_precedent) as mntprec, sum(bl.mnts_precedentexe) as mntprec2,sum(bl.mnts_budgetise) as montant
			FROM ref_titre rt, ref_section rs, ref_chapitre rc, ref_article ra, ref_paragraphe rp, budg_titre bt, budg_section bs, budg_chapitre bc,
			budg_param_article ba, budg_paragraphe bp, budg_ligne_budgetaire bl, budg_rubrique br
			WHERE rt.id = bt.titre AND rs.id = bs.section AND rc.id = bc.chapitre AND rp.id = bp.paragraphe AND ra.id = ba.article AND
			bt.id = bl.cd_titre_id AND bs.id = bl.cd_section_id AND bc.id = bl.cd_chapitre_id AND ba.id = bl.cd_article_id AND bp.id = bl.cd_paragraphe_id 
			AND br.id = bl.cd_rubrique_id AND bl.x_exercice_id = %s AND bl.company_id = %s AND bl.budg_id = %s
			group by rt.cd_titre , rs.cd_section, rc.cd_chapitre, ra.cd_article, 
			rp.cd_paragraphe, rp.lb_long order by titre asc """ ,(val_ex, val_struct, val_b))
            rows = vals.env.cr.dictfetchall()
            result = []
            
            vals.budg_budget_agrege_ids.unlink()
            for line in rows:
                result.append((0,0, {'titre_id' : line['titre'], 'section_id': line['section'], 'chapitre_id': line['chapitre'], 'article_id': line['article'],'paragraphe_id': line['para'], 'nature': line['nature'],'montant': line['mnt11'],'montant11': line['mnt11'], 'montant2': line['mnt2'], 'montant22': line['mnt22'],'montantp': line['mntprec'],'montantp2': line['mntprec2'],'montant': line['montant']}))
            self.budg_budget_agrege_ids = result

    
class BudgBudgetAgregeLine(models.Model):   
	_name = 'budg_budget_agrege_line'
    
	budget_id = fields.Many2one('budg_budget_agrege', ondelete='cascade')
	titre_id = fields.Char('Titre', readonly=True)
	section_id = fields.Char('Section', readonly=True)
	chapitre_id = fields.Char('Chapitre', readonly=True)
	article_id = fields.Char('Article', readonly=True)
	paragraphe_id = fields.Char('Paragraphe', readonly=True)
	nature = fields.Char("Nature", readonly=True)
	montant1 = fields.Float('Ex n-3 Prévision', readonly=True)
	montant11 = fields.Float('Ex n-3 Exécution', readonly=True)
	montant2 = fields.Float('Ex n-2 Prévision', readonly=True)
	montant22 = fields.Float('Ex n-2 Exécution', readonly=True)
	montantp = fields.Float('Ex n-1 Prévision', readonly=True)
	montantpp = fields.Float('Ex n-1 Exécution', readonly=True)
	montant = fields.Float('Montant', readonly=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)


class BudgTypeSignataire(models.Model):
	_name = 'budg_type_signataire'
	
	code = fields.Char("Code", required=True)
	name = fields.Char("Libellé", required=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)	

			
class  BudgJustDepense(models.Model):
	_name ='budg_just_depense'
	
	param_article_id = fields.Many2one("budg_param_article")
	lb_long = fields.Char("Libellé")
	oblige = fields.Boolean("Obligé")
	nombre = fields.Integer("Référence")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class  BudgJustRecette(models.Model):
	_name ='budg_just_recette'
	
	param_article_id = fields.Many2one("budg_param_article")
	lb_long = fields.Char("Libellé")
	oblige = fields.Boolean("Obligé")
	nombre = fields.Integer("Référence")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
		


class BudgCategoriePrecompte(models.Model):
	_name = "budg_categorie_precompte"
	_rec_name = "lb_long"

	lb_court = fields.Char("Libellé court")
	lb_long = fields.Char("Libellé long")
	active = fields.Boolean("Actif")

class BudgTypePrecompte(models.Model):
	_name = "budg_type_precompte"
	_rec_name = "lb_long"
	
	categorie_id = fields.Many2one("budg_categorie_precompte", "Catégorie de précompte")
	lb_court = fields.Char("Libellé court")
	lb_long = fields.Char("Libellé long")
	no_imputation = fields.Many2one("compta_plan_line", "Imputation")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

	

class BudgPrecompte(models.Model):
	_name = "budg_precompte"
	_rec_name = "no_precompte"
	
	no_precompte = fields.Char("N° Précompte")
	type_precompte = fields.Many2one("budg_type_precompte","Type de précompte", required=True)
	mnt_precompte = fields.Float("Montant précompte")
	reste = fields.Float("Reste")
	imput_budg = fields.Char("Imput Budg.", readonly=True)
	mnt_mandat = fields.Float("Montant", readonly=True)
	dt_mandat = fields.Date('Date', readonly=True)
	no_mdt = fields.Many2one('budg_mandat', "Référence mandat")
	no_lo = fields.Char('N° Liq', readonly=True)
	no_eng = fields.Char('N° Eng', readonly=True)
	objet = fields.Text('Objet', readonly=True)
	modereg = fields.Char("Mode de règlement", readonly=True)
	dt_precompte = fields.Date("Date précompte")
	objet_precompte = fields.Text("Objet du précompte", required=True)
	cpte_deb = fields.Many2one("compta_plan_line", "Cpte Débit", readonly=True)
	cpte_deb_id = fields.Integer()
	cpte_cred = fields.Many2one("compta_plan_line", "Cpte Crédit", readonly=True)
	cpte_cred_id = fields.Integer()
	dt_visa = fields.Date()
	state = fields.Selection([
		('N', 'Nouveau'),
		('P', 'Provisoire'),
		], string="Etat", default='N')
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)


class BudgReimputationDepense(models.Model):
	_name = 'budg_reimputation_depense'
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	reimputation_depense_ids = fields.One2many("budg_reimputation_depense_line","reimputationdep_id")

class BudgReimputationDepenseLine(models.Model):
	_name = 'budg_reimputation_depense_line'
	
	reimputationdep_id = fields.Many2one("budg_reimputation_depense")
	dte_mandat = fields.Date("Date de mandat")
	numero_mandat = fields.Many2one("budg_mandat", "Numéro Mdt")
	numero_bord = fields.Many2one("budg_bordereau_mandatement", "N° Bordereau")
	nature_depense = fields.Char("Nature dépense")
	imput_init = fields.Char("Imputation initiale")
	imput_def = fields.Char("Imputation définitive")
	montant = fields.Float("Montant")
	observation = fields.Text("Observation")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	

class BudgReimputationRecette(models.Model):
	_name = 'budg_reimputation_recette'
	
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	reimputation_recette_ids = fields.One2many("budg_reimputation_recette_line","reimputationrec_id")

class BudgReimputationRecetteLine(models.Model):
	_name = 'budg_reimputation_recette_line'
	
	reimputationrec_id = fields.Many2one("budg_reimputation_recette")
	dte_titre = fields.Date("Date de titre")
	numero_titre = fields.Many2one("budg_titrerecette", "Numéro Titre")
	numero_bord = fields.Many2one("budg_bord_titre_recette", "N° Bordereau")
	nature_titre = fields.Char("Nature titre")
	imput_init = fields.Char("Imputation initiale")
	imput_def = fields.Char("Imputation définitive")
	montant = fields.Float("Montant")
	observation = fields.Text("Observation")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	

class BudgEtatDepEng(models.Model):
	_name = 'budg_etat_depense_engage'
	_rec_name="section_id"
	
	dt_appro_deb = fields.Date("Du", required=True)
	dt_appro_fin = fields.Date("Au", required=True)
	section_id = fields.Char("Section",default="Fonctionnement", readonly=True)
	etadep_ids = fields.One2many("budg_etat_depense_engage_line", "etat_dep_id")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
	
	def rechercher(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		val_deb = str(self.dt_appro_deb)
		val_fin = str(self.dt_appro_fin)

		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT  e.no_eng as eng, b.nm as creancier, (e.mnt_eng - m.mnt_ord) as montant,e.dt_etat as dte, rp.cd_paragraphe as imputation
			FROM budg_engagement e, budg_paragraphe p, budg_mandat m,ref_beneficiaire b, ref_paragraphe rp
			WHERE rp.id = p.paragraphe and p.id = e.cd_paragraphe_id AND e.x_exercice_id = %s AND e.company_id = %s AND b.id = e.no_beneficiaire
			AND e.dt_etat BETWEEN %s and %s AND e.no_eng = m.no_eng AND b.id = e.no_beneficiaire and e.lbsection = 'FONCT' """ ,(val_ex, val_struct,val_deb, val_fin))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.etadep_ids.unlink()
			for line in rows:
				result.append((0,0, {'no_eng' : line['eng'], 'creancier': line['creancier'], 'imputation': line['imputation'], 'dte': line['dte'], 'montant': line['montant']}))
			self.etadep_ids = result

class BudgEtatDepEngLine(models.Model):
	_name ="budg_etat_depense_engage_line"
	
	
	etat_dep_id = fields.Many2one("budg_etat_depense_engage")
	no_eng = fields.Char("N° Acte d'Eng.")
	creancier = fields.Char('Créancier')
	imputation = fields.Char("Imputation")
	dte = fields.Date("Date")
	montant = fields.Float("Montant engagé non mandaté")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	

class BudgEtatRest(models.Model):
	_name = 'budg_etat_rest'
	_rec_name= "section_id"
	
	section_id = fields.Char("Section",default="Investissement", readonly=True)
	rest_ids = fields.One2many("budg_etat_rest_line", "rest_id")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
	def rechercher(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)

		
		for vals in self:
			vals.env.cr.execute("""SELECT DISTINCT br.lb_long as nature, l.mnt_corrige as budget, l.mnt_engage as realiser, (l.mnt_corrige - l.mnt_engage) as rest FROM budg_rubrique br, budg_ligne_exe_dep l, budg_engagement e, ref_section rs, budg_section bs 
			WHERE br.id = l.cd_rubrique_id AND rs.id = bs.section and bs.id = br.cd_section_id and rs.lb_court = 'INVEST' AND l.x_exercice_id = %d AND l.company_id = %d;""" %(val_ex, val_struct))
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.rest_ids.unlink()
			for line in rows:
				result.append((0,0, {'nature' : line['nature'], 'budget': line['budget'], 'realisation': line['realiser'], 'reste': line['rest']}))
			self.rest_ids = result
			
			for x in self.rest_ids:
				x.reste = x.budget - x.realisation

class BudgEtatRestLine(models.Model):
	_name ="budg_etat_rest_line"
	
	
	rest_id = fields.Many2one("budg_etat_rest")
	nature = fields.Char("Nature de l'investissement")
	budget = fields.Float('Budget')
	realisation = fields.Float("Réalisation")
	reste = fields.Float("Reste à réaliser")
	observation = fields.Text("Proposition de l'ordonnateur")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
class BudgAnnulMandat(models.Model):
	_name = 'budg_mandat_annule'
	_rec_name = 'mandat_id'
	
	mandat_id = fields.Many2one('budg_mandat', "Mandat à annuler", required=True)
	montant = fields.Float('Montant', readonly=True)
	dte_mandat = fields.Date("Date du mandat", readonly=True)
	dte_annulation = fields.Date("Date d'annulation", required=True)
	titre_id = fields.Many2one("budg_titre","Titre", readonly=True)
	section_id = fields.Many2one("budg_section","Section", readonly=True)
	chapitre_id = fields.Many2one("budg_chapitre","Chapitre", readonly=True)
	article_id = fields.Many2one("budg_param_article","Article", readonly=True)
	paragraphe_id = fields.Many2one("budg_paragraphe","Paragraphe", readonly=True)
	rubrique_id = fields.Many2one("budg_rubrique","Rubrique", readonly=True)
	objet = fields.Text("Objet", readonly=True)
	typebenef = fields.Many2one("ref_typebeneficiaire","Type de bénéficiaire", readonly=True)
	nom = fields.Char("Bénéficiaire", readonly=True)
	motif = fields.Text("Motif d'annulation", required=True)
	no_lo = fields.Many2one("budg_liqord","Liquidation", readonly=True)
	no_eng = fields.Many2one("budg_engagement", "Engagement", readonly=True)
	state = fields.Selection([
		('N', 'Nouveau'),
		('A', 'Annulé'),
		('WA', 'Visa CF'),
		], string= 'Etat', default='N')
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
	@api.onchange('mandat_id')
	def OnChangeMdt(self):
		if self.mandat_id:
			self.montant = self.mandat_id.mnt_ord
			self.dte_mandat = self.mandat_id.dt_etat
			self.objet = self.mandat_id.obj
			self.typebenef = self.mandat_id.type_beneficiaire_id
			self.nom = self.mandat_id.no_beneficiaire
			self.titre_id = self.mandat_id.cd_titre_id
			self.section_id = self.mandat_id.cd_section_id
			self.chapitre_id = self.mandat_id.cd_chapitre_id
			self.article_id = self.mandat_id.cd_article_id
			self.paragraphe_id = self.mandat_id.cd_paragraphe_id
			self.rubrique_id = self.mandat_id.cd_rubrique_id
			self.no_lo = self.mandat_id.no_lo
			self.no_eng = self.mandat_id.no_lo.no_eng
	
	
	def annuler(self):
		
		v_ex = int(self.x_exercice_id)
		v_struct = int(self.company_id)
		v_mdt = int(self.mandat_id)
		v_nolo = int(self.no_lo)
		v_eng = int(self.no_eng)

		self.env.cr.execute("""UPDATE budg_mandat SET state = 'A' WHERE x_exercice_id = %d AND company_id = %s AND id = %d""" %(v_ex, v_struct, v_mdt))
	
		self.env.cr.execute("""UPDATE budg_liqord SET state = 'A' WHERE x_exercice_id = %d AND company_id = %s AND id = %d""" %(v_ex, v_struct, v_nolo))

		self.env.cr.execute("""UPDATE budg_engagement SET state = 'V' WHERE x_exercice_id = %s AND company_id = %s AND id = %s """ , (v_ex, v_struct, v_eng))


		self.action_mandat_annuler()

	@api.multi
	def action_mandat_annuler(self):
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		v_mdt = int(self.mandat_id)

		val_titre = int(self.titre_id)
		val_chap = int(self.chapitre_id)
		val_sec = int(self.section_id)
		val_art = int(self.article_id)
		val_par = int(self.paragraphe_id)
		val_rub = int(self.rubrique_id)


		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET mnt_mandate = (select DISTINCT sum(BM.mnt_ord) - BM.mnt_ord
			FROM budg_ligne_exe_dep BE, budg_mandat BM WHERE BM.id = %d AND 
			BE.cd_titre_id = %d and BE.cd_section_id = %d and BE.cd_chapitre_id = %d and BE.cd_art_id = %d and BE.cd_paragraphe_id = %d and 
			BE.cd_rubrique_id = %d and BE.x_exercice_id = %d and BE.company_id = %d group by  BM.mnt_ord) WHERE cd_titre_id = %d and 
			cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d and 
			cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d""" % (v_mdt,
		val_titre, val_sec, val_chap, val_art, val_par, val_rub, val_ex, val_struct, val_titre, val_sec, val_chap,
		val_art, val_par, val_rub, val_ex, val_struct))

		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET reste_mandat = (mnt_corrige - mnt_mandate) + mnt_mandate
			WHERE cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d and cd_paragraphe_id = %d 
			and cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d""" % (
		val_titre, val_sec, val_chap, val_art, val_par, val_rub, val_ex, val_struct))

		self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET taux = ((mnt_mandate * 100) / mnt_corrige)
			WHERE cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_art_id = %d 
			and cd_paragraphe_id = %d and cd_rubrique_id = %d and x_exercice_id = %d and company_id = %d""" % (
		val_titre, val_sec, val_chap, val_art, val_par, val_rub, val_ex, val_struct))

		self.write({'state': 'A'})
		
	@api.multi
	def viser(self):
		self.write({'state' : 'WA'})
		

class BudgBordManAnnul(models.Model):

	_name = "budg_bordereau_mandat_annule"
	_rec_name = "type_bord_trsm"

	type_bord_trsm = fields.Char('Type de bordereau', readonly=True)
	cd_acteur = fields.Char(string ="Acteur", readonly=True)
	date_emis = fields.Date(string="Date d'émission",default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception", readonly=True)
	num_accuse = fields.Char()
	totaux = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	cd_acteur_accuse = fields.Char(string ="Acteur", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	mandat_ids = fields.Many2many("budg_mandat_annule", "budg_detail_bord_mandat_annule", string="Liste des mandats annulés")
	state = fields.Selection([
        ('N', 'Nouveau'),
        ('V', 'Mise en bordereau'),
        ('R', 'Reception Bord. Annul.'),
        ('ED', 'Renvoi bord. CF/CG'),
        ('RD', 'Reception bord CF/CG'),
        ], 'Etat', default='N', required=True, readonly=True)
	
	@api.multi
	def MiseBord(self):
		
		val_struct = int(self.company_id)
		val_ex = int(self.x_exercice_id)
		val_id = int(self.id)
		
		self.env.cr.execute("""SELECT sum(montant) FROM budg_mandat_annule m, budg_bordereau_mandat_annule b, budg_detail_bord_mandat_annule bm
		WHERE b.x_exercice_id = %d AND b.company_id = %d AND bm.budg_bordereau_mandat_annule_id = %d
		AND m.id = bm.budg_mandat_annule_id AND bm.budg_bordereau_mandat_annule_id = b.id""" %(val_ex,val_struct, val_id))
		res = self.env.cr.fetchone()
		self.totaux = res and res[0]

		self.env.cr.execute("select lb_long from budg_typebordtrans where code = '10' ")
		val = self.env.cr.fetchone()
		self.type_bord_trsm = val and val[0] or 0
		
		self.env.cr.execute("select type_depart from budg_typebordtrans where code = '10' ")
		val1 = self.env.cr.fetchone()
		self.cd_acteur = val1 and val1[0] or 0
		
		self.env.cr.execute("select type_dest from budg_typebordtrans where code = '10' ")
		val2 = self.env.cr.fetchone()
		self.cd_acteur_accuse = val2 and val2[0] or 0

		
		self.write({'state' : 'V'})
		
	@api.multi
	def RecBord(self):
		self.write({'state' : 'R'})
		
	@api.multi
	def RenBord(self):
		self.write({'state' : 'ED'})
	
	@api.multi
	def ReceBord(self):
		self.write({'state' : 'RD'})
		
	@api.depends('totaux')
	def amount_to_words(self):
		self.text_amount = num2words(self.totaux, lang='fr')
		

class BudgRecetteAnnule(models.Model):
	_name = 'budg_recette_annule'
	_rec_name = "recette_id"
	
	recette_id = fields.Many2one('budg_titrerecette', "Titre à annuler ou à réduire", required=True)
	montant = fields.Float('Montant', readonly=True)
	dte_titre = fields.Date("Date d'émission du titre de recette", readonly=True)
	dte_annulation = fields.Date("Date d'annulation ou de réduction", required=True)
	titre_id = fields.Char("Titre", readonly=True)
	section_id = fields.Char("Section", readonly=True)
	chapitre_id = fields.Char("Chapitre", readonly=True)
	article_id = fields.Char("Article", readonly=True)
	paragraphe_id = fields.Char("Paragraphe", readonly=True)
	rubrique_id = fields.Char("Rubrique", readonly=True)
	objet = fields.Text("Objet", readonly=True)
	typedebiteur = fields.Char("Type de débiteur", readonly=True)
	nom = fields.Char("Nom débiteur", readonly=True)
	motif = fields.Text("Motif d'annulation", required=True)
	no_lo = fields.Integer()
	state = fields.Selection([
		('N', 'Nouveau'),
		('A', 'Annulé'),
		('W', 'Visa CF'),
		], string= 'Etat', default='N')
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	
	@api.onchange('recette_id')
	def OnChangerec(self):
		if self.recette_id:
			self.montant = self.recette_id.mnt_rec
			self.dte_titre = self.recette_id.dt_rec
			self.objet = self.recette_id.lb_objet
			self.typedebiteur = self.recette_id.cd_type_contribuable.lb_long
			self.nom = self.recette_id.contribuable_id.nm_rs
			self.titre_id = self.recette_id.cd_titre_id.titre.titre
			self.section_id = self.recette_id.cd_section_id.section.section
			self.chapitre_id = self.recette_id.cd_chapitre_id.chapitre.chapitre
			self.article_id = self.recette_id.cd_article_id.article.article
			self.paragraphe_id = self.recette_id.cd_paragraphe_id.paragraphe.paragraphe
			self.rubrique_id = self.recette_id.cd_rubrique_id.concate_rubrique
			
	def annuler(self):
		
		v_ex = int(self.x_exercice_id)
		v_struct = int(self.company_id)
		v_rec = int(self.recette_id)
		self.env.cr.execute("""UPDATE budg_titrerecette SET et_doss = 'A' WHERE x_exercice_id = %s AND company_id = %s AND id = %d""" %(v_ex, v_struct, v_rec))
	
		self.write({'state': 'A'})


class Budg_bord_titreAnnule(models.Model):
	
	_name = "budg_bord_titre_recette_annule"
	_rec_name = "no_bord_rec"
	
	name = fields.Char()
	no_bord_rec = fields.Char("N° Bord", readonly=True)
	cd_acteur = fields.Selection([
        ('ORD', 'ORD'),
        ('CF', 'CF'),
        ('AC', 'AC'),
        ], string ="Acteur", default="ORD")
	date_emis = fields.Date("Date bordereau", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date()
	num_accuse = fields.Char()
	totaux = fields.Float()
	type_bord_trsm = fields.Char("Type de bordereau", default="Bordereau d'annulation Titre de recette", readonly=True)
	cd_acteur_accuse = fields.Selection([
        ('ORD', 'ORD'),
        ('CF', 'CF'),
        ('AC', 'AC'),
        ], string ="Acteur accusé")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	recette_ids = fields.Many2many("budg_recette_annule", "budg_detail_bord_recette_annule", string="Liste des titres de recettes", ondelete="restrict")
	state = fields.Selection([
        ('N', 'Nouveau'),
        ('V', 'Mise en bordereau'),
		('R', 'Réception bord. Annul.'),
		('ED', 'Envoi bord. CF/CG'),
		('RD', 'Réception bord. CF/CG'),
        ], 'Etat', default='N', required=True)
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	
	@api.multi
	def MiseBord(self):
		self.write({'state' : 'V'})
		
	@api.multi
	def RecBord(self):
		self.write({'state' : 'R'})
		
	@api.multi
	def RenBord(self):
		self.write({'state' : 'ED'})
	
	@api.multi
	def ReceBord(self):
		self.write({'state' : 'RD'})
		
	@api.depends('totaux')
	def amount_to_words(self):
		self.text_amount = num2words(self.totaux, lang='fr')
 
 
class Ref_TypeContribuable(models.Model):

    _name = "ref_typecontribuable"
    _rec_name = "cate_id"

    sequence = fields.Integer(default=10)
    cd_type_contribuable = fields.Char(string = "Code", default=lambda self: self.env['ir.sequence'].next_by_code('cd_type_contribuable'), readonly = True)
    lb_long = fields.Char(string = "Libellé court", size = 25, required=False)
    name = fields.Char(string = "Libellé long", size = 100, required=False)
    active = fields.Boolean('Actif',default=True)
    cate_id = fields.Many2one("ref_categoriecontribuable", required=True,string = "Catégorie de contribuable")
    cpte_client = fields.Many2one("compta_plan_line",string = "Compte tiers", required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
        ('cd_type_contribuable', 'unique (cd_type_contribuable)', "Ce code existe déjà. Veuillez changer de code !"),
    ]

class BudgContribuable(models.Model):

    _name = "ref_contribuable"
    _rec_name = 'nm_rs'
    
    
    no_contrib = fields.Char(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('no_contrib'), readonly = True)
    type_contribuable_id = fields.Many2one("ref_typecontribuable",string="Type de contribuable", required=True)
    nm_rs = fields.Char(string="Intitulé", required=True)
    nm_rs2 = fields.Char(string=" ")
    an_agre = fields.Date(string="Année agrément")
    no_agre = fields.Integer(string="N° Agrément")
    no_ifu = fields.Text(string="Infos", size=11)
    cd_citib = fields.Char(string="Cd_CITIB")
    activite = fields.Char(string="Activité", size  = 50)
    ap_rue = fields.Char(string="Rue")
    ap_bp = fields.Char(string="Boite Postale")
    ap_cd_post = fields.Char(string="Code Postale")
    ap_region = fields.Many2one("ref_region",string="Région")
    ap_ville = fields.Char(string="Ville")
    ap_province = fields.Many2one("ref_province",string="Province")
    ap_pays = fields.Many2one("ref_pays",string="Pays")
    rf_txt_agre = fields.Char(string="Texte n°")
    dt_txt_agre = fields.Date(string="Du")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    bank_id = fields.Many2one("res.partner.bank", string = "Banque")
    fg_eng = fields.Char()
    active = fields.Boolean('Actif',default=True)
    agence_bank_id = fields.Char(string = "N° Agence")
    acc_number = fields.Char(string = "N° compte")
    tel = fields.Char(string="Téléphone")
    mail = fields.Char(string="Mail")
    cpte_client = fields.Many2one("ref_souscompte", string = "Compte tiers")
    cpte_fournisseur = fields.Many2one("ref_souscompte", string = "Compte tiers")



class ref_TypeBeneficiaire(models.Model):

    _name = "ref_typebeneficiaire"
    _rec_name = "cat_id"

    sequence = fields.Integer(default=10)
    cd_type_beneficiaire = fields.Char(string = "Code", size = 2)
    name = fields.Char(string = "Libellé court", size = 25, required=False)
    lb_long = fields.Char(string = "Libellé long", size = 100, required=False)
    cat_id = fields.Many2one("ref_categoriebeneficiaire", string = "Catégorie de bénéficiaire", required=True)
    cpte_client = fields.Many2one("compta_plan_line",string = "Compte tiers", required=True)
    active = fields.Boolean('Actif',default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)

    _sql_constraints = [
        ('cd_type_beneficiaire', 'unique (cd_type_beneficiaire)', "Ce code existe déjà. Veuillez changer de code !"),
    ]    
 

class RefBeneficiaire(models.Model):

    _name = "ref_beneficiaire"
    _rec_name = "nm"
    
    name = fields.Char(string="Identifiant", default=lambda self: self.env['ir.sequence'].next_by_code('name'), readonly = True)
    no_beneficiaire = fields.Char(string="Raison sociale", size=65)
    type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire",string="Catégorie de bénéficiaire", required=True)
    nm = fields.Char(string="Intitulé", required=True)
    pn = fields.Char(string="Prénom", size=40)
    no_ifu = fields.Char(string="N° IFU", size=20)
    domaine_id = fields.Many2one('ref_secteur_activite', "Domaine d'activité", required=False)
    cd_mat = fields.Char(string="Matricule", size=20)
    no_eng = fields.Integer(string="No_Eng")
    ex_last = fields.Integer(string="Ex_last")
    ap_rue = fields.Char(string="Rue", size=35)
    ap_bp = fields.Char(string="Boite postale", size=8)
    ap_cd_post = fields.Char(string="Code postal", size=6)
    ap_ville = fields.Char(string="Ville", size=30)
    ap_pays = fields.Many2one("ref_pays",string="Pays")
    tel = fields.Char(string="Téléphone", size=30)
    nm_officiel = fields.Char(string="Titre officiel", size=50)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
    bank_id = fields.Many2one("res.bank", string = "Banque")
    active = fields.Boolean('Actif',default=True)
    fg_bloc = fields.Char()
    cpte_client = fields.Many2one("ref_souscompte", string = "Compte tiers")
    cpte_fournisseur = fields.Many2one("compta_plan_line", string = "Compte tiers")
    agence_bank_id = fields.Char(string = "N° Agence")
    acc_number = fields.Char(string = "N° compte")
    cat_fournisseur = fields.Selection([
        ('S', 'Société'),
        ('P', 'Particulier')], 'Catégorie')
    

class BudgBordEngCtrl(models.Model):

	_name = "budg_bordereau_engagement_controle"
	_rec_name = "no_bord_en"

	no_bord_en = fields.Char(string='Bord. N°', readonly=True)
	type_bord_trsm = fields.Char("Type de bordereau", default="Bordereau de Reception d'Engagement de DAF/DCMEF", readonly=True)
	cd_acteur = fields.Char(string ="Acteur", default="DCMEF/CG", readonly=True)
	date_emis = fields.Date("Date émision", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date()
	num_accuse = fields.Char()
	totaux = fields.Integer()
	bord_recu = fields.Many2one("budg_bordereau_engagement", "N° Bord. reçu", required=True, domain=[('state','=','T')])
	cd_acteur_accuse = fields.Char(string ="Acteur")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	engagement_ids = fields.One2many("budg_liste_engagment", "bord_id")
	state = fields.Selection([
        ('N', 'Nouveau'),
        ('R', 'Réceptionner bordereau'),
        ('E', 'Envoyer à DAF/DFC'),
        ('BR', 'Bordereau réceptionné par DAF/DFC'),
        ], 'Etat', default='N', required=True)
	total_prec = fields.Integer()
	
	
	def afficher(self):
		
		id_bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		for vals in self:
			vals.env.cr.execute("""select b.dt_etat as dte, b.id as eng, b.cd_titre_id as titre, b.cd_section_id as sec, b.cd_chapitre_id as chap,
			b.cd_article_id as art, b.cd_paragraphe_id as par, b.cd_rubrique_id as rub, b.type_procedure as proc, b.type_beneficiaire_id as typeb,
			b.no_beneficiaire as benef, b.lb_obj as obj, b.mnt_eng as mnt from budg_engagement b, budg_bordereau_engagement bb, eng_id i
			where bb.id = %d and i.budg_engagement_id = b.id and i.budg_bordereau_engagement_id = bb.id and b.company_id = %d and b.x_exercice_id = %d and b.state = 'V' """ %(id_bord, val_struct, val_ex))
			
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.engagement_ids.unlink()
			for line in rows:
				result.append((0,0, {'dt_etat' : line['dte'], 'no_eng': line['eng'], 'cd_titre_id': line['titre'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'],'cd_article_id': line['art'],
									'cd_paragraphe_id': line['par'],'cd_rubrique_id': line['rub'],'type_procedure': line['proc'],'type_beneficiaire_id': line['typeb'],
									'no_beneficiaire': line['benef'],'lb_obj': line['obj'],'mnt_eng': line['mnt']}))
			self.engagement_ids = result
	
	def receptionner(self):
		
		bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		self.env.cr.execute("""UPDATE budg_bordereau_engagement SET state ='R' WHERE id = %d and x_exercice_id = %d and
		company_id = %d""" %(bord, val_ex, val_struct))

		self.env.cr.execute("select bordeng from budg_compteur_bord_eng_ctrl where x_exercice_id = %d and company_id = %d" % (val_ex, val_struct))
		bordeng = self.env.cr.fetchone()
		no_bord_en = bordeng and bordeng[0] or 0
		c1 = int(no_bord_en) + 1
		c = str(no_bord_en)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_bord_eng_ctrl(x_exercice_id,company_id,bordeng)  VALUES(%d, %d, %d)""" % (val_ex, val_struct, vals))
		else:
			c1 = int(no_bord_en) + 1
			c = str(no_bord_en)
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_bord_eng_ctrl SET bordeng = %d  WHERE x_exercice_id = %d and company_id = %d" % (vals, val_ex, val_struct))
		
		#self.afficher()
		
		self.write({'state': 'R'})
	
	
	def envoyer(self):
		
		self.write({'state': 'E'})
		
	

class BudgListeEngagement(models.Model):
	_name = 'budg_liste_engagment'
	
	
	bord_id = fields.Many2one('budg_bordereau_engagement_controle', ondelete='cascade')
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date", readonly =True)
	no_eng = fields.Many2one("budg_engagement" ,string="N° engagement", readonly=True)
	cd_titre_id = fields.Many2one("budg_titre", 'Titre',readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one("budg_typeprocedure", string = "Type de procédure", v=True)
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	no_beneficiaire = fields.Many2one("ref_beneficiaire", readonly=True, string = "Identité")
	lb_obj = fields.Text(string = "Objet",size=300, readonly=True)
	mnt_eng = fields.Float(string = "Montant engagement", readonly=True)
	piecejust_ids = fields.One2many("budg_liste_piece_eng",'eng_id', readonly=True)
	dt_visa_cf = fields.Date(string = "Date Visa")
	motif_rejet = fields.Selection([('1', 'Erreur Imputation'),
		('2','Erreur Montant'),('3','Erreur Pièce'),('4','Erreur Bénéficiaire'),
		('5','Erreur Objet')],string = "Motif du rejet")
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	state = fields.Selection([
		('V','Approuvé'),
		('W', 'Visé'),
		('R', 'Rejeté'),
        ], default='V', string='Etat',index=True,readonly=True, track_visibility='always')
	credit_disponible = fields.Integer()
	envoyer_daf = fields.Selection([('Y','Oui'),('N','Non')], string='Envoyé ?', default='Y')
	
	
	def viser(self):
		
		for vals in self:
		
			eng = int(vals.no_eng)
			val_ex = int(vals.x_exercice_id)
			val_strcut = int(vals.company_id)
			if self.envoyer_daf == 'Y':
				self.env.cr.execute("""UPDATE budg_engagement SET state ='W', envoyer_daf = 'Y' WHERE id = %d and company_id = %d and
				x_exercice_id = %d""" %(eng, val_strcut, val_ex))
			else:
				self.env.cr.execute("""UPDATE budg_engagement SET state ='W' WHERE id = %d and company_id = %d and
				x_exercice_id = %d""" %(eng, val_strcut, val_ex))
				
			
			self.write({'state': 'W'})
	
	def rejeter(self):
		
		eng = int(self.no_eng)
		val_ex = int(self.x_exercice_id)
		val_strcut = int(self.company_id)
		
		self.env.cr.execute("""UPDATE budg_engagement SET state ='R' WHERE id = %d and x_exercice_id = %d and
		company_id = %d""" %(eng, val_ex, val_strcut ))
		
		self.write({'state': 'R'})
			
	
	
	def afficher_piece(self):
		
		eng = int(self.no_eng)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		for vals in self:
			vals.env.cr.execute("select lb_long as lib, oblige as obl, ref as re, montant as mnt, nombre as nbr from budg_piece_engagement where eng_id = %d and company_id = %d and x_exercice_id = %d" %(eng, val_struct, val_ex))
		
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.piecejust_ids.unlink()
			for line in rows:
				result.append((0,0, {'lib' : line['lib'], 'oblige': line['obl'], 'ref': line['re'], 'mnt': line['mnt'], 'nbr': line['nbr']}))
			self.piecejust_ids = result
			
	
class BudgListePieceEng(models.Model):
	_name = "budg_liste_piece_eng"
	
	eng_id = fields.Many2one("budg_liste_engagment", ondelete='cascade')
	lib = fields.Many2one("budg_typepjbudget","Libellé", readonly=True)
	oblige = fields.Boolean("Obligatoire", readonly=True)
	ref = fields.Char("Référence", readonly=True)
	nbr = fields.Integer("Nombre", readonly=True)
	mnt = fields.Integer("Montant", readonly=True)
	
	
	

class BudgBordEngRejetCtrl(models.Model):

	_name = "budg_bordereau_engagement_rejet_controle"
	_rec_name = "no_bord_en"

	no_bord_en = fields.Char(string='Bord. N°', readonly=True)
	type_bord_trsm = fields.Char("Type de bordereau", default='Bordereau de rejet', readonly=True)
	cd_acteur = fields.Char(string ="Acteur", default='DCMEF/CG', readonly=True)
	date_emis = fields.Date("Date émision", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date()
	num_accuse = fields.Char()
	totaux = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	cd_acteur_accuse = fields.Char(string ="Acteur")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	engagement_ids = fields.Many2many("budg_engagement", "engagement_rejeter", domain=[('state','=','R')], string="Liste des engagements", ondelete="restrict")
	state = fields.Selection([
        ('N', 'Nouveau'),
		('E', 'Envoyé à DAF/DFC'),
		('R', 'Réceptionné par DAF/DFC'),
        ], 'Etat', default='N', required=True)
	total_prec = fields.Integer()

#Reception du bordereau envoyer par dcmef/cg
class BudgBordEngRecepCtrl(models.Model):

	_name = "budg_bordereau_engagement_recep_controle"
	_rec_name = "no_bord_en"

	no_bord_en = fields.Char(string='Bord. N°', readonly=True)
	type_bord_trsm = fields.Char("Type de bordereau", default="Bordereau de Reception d'Engagement de DMCEF/CG", readonly=True)
	cd_acteur = fields.Char(string ="Acteur", default='DAF/DFC', readonly=True)
	bord_recu = fields.Many2one("budg_bordereau_engagement_renvoi_daf","N° Bord. réçu",required=True, domain=[('state','=','E')])
	date_emis = fields.Date("Date émision", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date()
	num_accuse = fields.Char()
	totaux = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	cd_acteur_accuse = fields.Char(string ="Acteur")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	engagement_ids = fields.Many2many("budg_liste_engagment_recu", "bord_id", string="Liste des engagements", ondelete="restrict")
	state = fields.Selection([
		('E', 'Bordereau envoyé par DCMEF/CG'),
		('R', 'Réceptionné bordereau DCMEF/CG'),
        ], 'Etat', default='E', required=True)
	total_prec = fields.Integer()


	def afficher(self):
		
		id_bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		if self.bord_recu:
		
			for vals in self:
				vals.env.cr.execute("""select b.dt_etat as dte, b.no_eng as eng, b.cd_titre_id as titre, b.cd_section_id as sec, b.cd_chapitre_id as chap,
				b.cd_article_id as art, b.cd_paragraphe_id as par, b.cd_rubrique_id as rub, b.type_procedure as proc, b.type_beneficiaire_id as typeb,
				b.no_beneficiaire as benef, b.lb_obj as obj, b.mnt_eng as mnt from budg_liste_engagment_renvoi b 
				where b.bord_id = %d and b.company_id = %d and b.x_exercice_id = %d and b.state = 'V' """ %(id_bord, val_struct, val_ex))
				
				rows = vals.env.cr.dictfetchall()
				result = []
				
				vals.engagement_ids.unlink()
				for line in rows:
					result.append((0,0, {'dt_etat' : line['dte'], 'no_eng': line['eng'], 'cd_titre_id': line['titre'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'],'cd_article_id': line['art'],
										'cd_paragraphe_id': line['par'],'cd_rubrique_id': line['rub'],'type_procedure': line['proc'],'type_beneficiaire_id': line['typeb'],
										'no_beneficiaire': line['benef'],'lb_obj': line['obj'],'mnt_eng': line['mnt']}))
				self.engagement_ids = result

	
	def receptionner(self):
		
		bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		self.env.cr.execute("""UPDATE budg_bordereau_engagement_renvoi_daf SET state ='R' WHERE id = %d and x_exercice_id = %d and
		company_id = %d""" %(bord, val_ex, val_struct))

		self.env.cr.execute("select bordeng from budg_compteur_bord_eng_recep where x_exercice_id = %d and company_id = %d" % (val_ex, val_struct))
		bordeng = self.env.cr.fetchone()
		no_bord_en = bordeng and bordeng[0] or 0
		c1 = int(no_bord_en) + 1
		c = str(no_bord_en)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_bord_eng_recep(x_exercice_id,company_id,bordeng)  VALUES(%d, %d, %d)""" % (val_ex, val_struct, vals))
		else:
			c1 = int(no_bord_en) + 1
			c = str(no_bord_en)
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_bord_eng_recep SET bordeng = %d  WHERE x_exercice_id = %d and company_id = %d" % (vals, val_ex, val_struct))
		
		self.afficher()
		
		self.write({'state': 'R'})

	

class BudgListeEngagementRecu(models.Model):
	_name = 'budg_liste_engagment_recu'
	
	
	bord_id = fields.Many2one('budg_bordereau_engagement_recep_controle', ondelete='cascade')
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date", readonly =True)
	no_eng = fields.Many2one("budg_engagement" ,string="N° engagement", readonly=True)
	cd_titre_id = fields.Many2one("budg_titre", 'Titre',readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one("budg_typeprocedure", string = "Type de procédure", v=True)
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	no_beneficiaire = fields.Many2one("ref_beneficiaire", readonly=True, string = "Identité")
	lb_obj = fields.Text(string = "Objet",size=300, readonly=True)
	mnt_eng = fields.Float(string = "Montant engagement", readonly=True)
	dt_visa_cf = fields.Date(string = "Date Visa")
	motif_rejet = fields.Selection([('1', 'Erreur Imputation'),
		('2','Erreur Montant'),('3','Erreur Pièce'),('4','Erreur Bénéficiaire'),
		('5','Erreur Objet')],string = "Motif du rejet")
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	state = fields.Selection([
		('V','Approuvé'),
		('W', 'Visé'),
		('R', 'Rejeté'),
        ], default='V', string='Etat',index=True,readonly=True, track_visibility='always')
	credit_disponible = fields.Integer()
	envoyer_daf = fields.Selection([('Y','Oui'),('N','Non')], string='Envoyé ?', default='Y')



class BudgBordEngRenvoiDaf(models.Model):

	_name = "budg_bordereau_engagement_renvoi_daf"
	_rec_name = "no_bord_en"

	no_bord_en = fields.Char(string='Bord. N°', readonly=True)
	type_bord_trsm = fields.Char("Type de bordereau", default="Bordereau de Transmission d'Engament pour DAF/DFC", readonly=True)
	cd_acteur = fields.Char(string ="Acteur", default='DCMEF/CG', readonly=True)
	bord_recu = fields.Many2one("budg_bordereau_engagement_controle","N° Bord.",required=True, domain=[('state','=','R')])
	date_emis = fields.Date("Date émision", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date()
	num_accuse = fields.Char()
	totaux = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency", readonly=True)
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words" )
	cd_acteur_accuse = fields.Char(string ="Acteur")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	engagement_ids = fields.One2many("budg_liste_engagment_renvoi", "bord_id", string="Liste des engagements")
	state = fields.Selection([
		('N', 'Nouveau'),
		('E', 'Envoyé bordereau à DAF/DFC'),
		('R', 'Bordereau receptionné par DAF/DFC'),
        ], 'Etat', default='N', required=True)
	total_prec = fields.Integer()


	def afficher(self):
		
		id_bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		for vals in self:
			vals.env.cr.execute("""select b.dt_etat as dte, b.no_eng as eng, b.cd_titre_id as titre, b.cd_section_id as sec, b.cd_chapitre_id as chap,
			b.cd_article_id as art, b.cd_paragraphe_id as par, b.cd_rubrique_id as rub, b.type_procedure as proc, b.type_beneficiaire_id as typeb,
			b.no_beneficiaire as benef, b.lb_obj as obj, b.mnt_eng as mnt from budg_liste_engagment b 
			where b.bord_id = %d and b.company_id = %d and b.x_exercice_id = %d and b.state = 'W' and b.envoyer_daf = 'Y' """ %(id_bord, val_struct, val_ex))
			
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.engagement_ids.unlink()
			for line in rows:
				result.append((0,0, {'dt_etat' : line['dte'], 'no_eng': line['eng'], 'cd_titre_id': line['titre'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'],'cd_article_id': line['art'],
									'cd_paragraphe_id': line['par'],'cd_rubrique_id': line['rub'],'type_procedure': line['proc'],'type_beneficiaire_id': line['typeb'],
									'no_beneficiaire': line['benef'],'lb_obj': line['obj'],'mnt_eng': line['mnt']}))
			self.engagement_ids = result
	
	
	def envoyer(self):
		
		bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		self.env.cr.execute("""UPDATE budg_bordereau_engagement_controle SET state ='BR' WHERE id = %d and x_exercice_id = %d and
		company_id = %d""" %(bord, val_ex, val_struct))

		self.env.cr.execute("select bordeng from budg_compteur_bord_eng_renvoi where x_exercice_id = %d and company_id = %d" % (val_ex, val_struct))
		bordeng = self.env.cr.fetchone()
		no_bord_en = bordeng and bordeng[0] or 0
		c1 = int(no_bord_en) + 1
		c = str(no_bord_en)
		if c == "0":
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("""INSERT INTO budg_compteur_bord_eng_renvoi(x_exercice_id,company_id,bordeng)  VALUES(%d, %d, %d)""" % (val_ex, val_struct, vals))
		else:
			c1 = int(no_bord_en) + 1
			c = str(no_bord_en)
			ok = str(c1).zfill(4)
			self.no_bord_en = ok
			vals = c1
			self.env.cr.execute("UPDATE budg_compteur_bord_eng_renvoi SET bordeng = %d  WHERE x_exercice_id = %d and company_id = %d" % (vals, val_ex, val_struct))
		
		#self.afficher()
		
		self.write({'state': 'E'})

	

class BudgListeEngagementRenvoi(models.Model):
	_name = 'budg_liste_engagment_renvoi'
	
	
	bord_id = fields.Many2one('budg_bordereau_engagement_renvoi_daf', ondelete='cascade')
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date", readonly =True)
	no_eng = fields.Many2one("budg_engagement" ,string="N° engagement", readonly=True)
	cd_titre_id = fields.Many2one("budg_titre", 'Titre',readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one("budg_typeprocedure", string = "Type de procédure", v=True)
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	no_beneficiaire = fields.Many2one("ref_beneficiaire", readonly=True, string = "Identité")
	lb_obj = fields.Text(string = "Objet",size=300, readonly=True)
	mnt_eng = fields.Float(string = "Montant engagement", readonly=True)
	dt_visa_cf = fields.Date(string = "Date Visa")
	motif_rejet = fields.Selection([('1', 'Erreur Imputation'),
		('2','Erreur Montant'),('3','Erreur Pièce'),('4','Erreur Bénéficiaire'),
		('5','Erreur Objet')],string = "Motif du rejet")
	x_exercice_id = fields.Many2one("ref_exercice",  default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	state = fields.Selection([
		('V','Approuvé'),
		('W', 'Visé'),
		('R', 'Rejeté'),
        ], default='V', string='Etat',index=True,readonly=True, track_visibility='always')
	credit_disponible = fields.Integer()



class BudgBordMdtControle(models.Model):
	_name = "budg_bordereau_mandatement_controle_a_viser"
	_rec_name = "no_bord_mandat"

	name = fields.Char()
	no_bord_mandat = fields.Char("Bord. N°", readonly=True)
	type_bord_trsm = fields.Char('Type de bordereau',default='Bordereau de Réception de Mandats de DAF/ORD', readonly=True)
	cd_acteur = fields.Char(string="Acteur", default="DCMEF/CG",readonly=True)
	date_emis = fields.Date(string="Date d'émission", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception", readonly=True)
	num_accuse = fields.Char()
	bord_recu = fields.Many2one("budg_bordereau_mandatement", required=True, domain=[('et_doss','=','V')])
	totaux = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",readonly=True)
	cd_acteur_accuse = fields.Char(string="Acteur",  default="DAF/DFC", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	mandat_ids = fields.One2many("budg_liste_mandatement", "liste_id")
	et_doss = fields.Selection([
		('N', 'Nouveau'),
		('R', 'Receptionné'),
		('E', 'Envoyé à la DAF/DFC '),
	], 'Etat', default='N', required=True)
	total_prec = fields.Integer()
	

	def afficher(self):
		
		id_bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		if self.bord_recu:
		
			for vals in self:
				vals.env.cr.execute("""select m.dt_etat as dte,m.no_lo as liq, m.id as mdt, m.cd_titre_id as titre, m.cd_section_id as sec, m.cd_chapitre_id as chap,
				m.cd_article_id as art, m.cd_paragraphe_id as par, m.cd_rubrique_id as rub, m.type_procedure as proc, m.type_beneficiaire_id as typeb,
				m.no_beneficiaire as benef, m.obj as obj, m.mnt_ord as mnt from budg_mandat m, budg_bordereau_mandatement bb, budg_detail_bord_mandat i
				where bb.id = %d and i.budg_mandat_id = m.id and i.budg_bordereau_mandatement_id = bb.id and m.company_id = %d
				and m.x_exercice_id = %d and m.state = 'O' """ %(id_bord, val_struct, val_ex))
				
				rows = vals.env.cr.dictfetchall()
				result = []
				
				vals.mandat_ids.unlink()
				for line in rows:
					result.append((0,0, {'dt_etat' : line['dte'], 'no_lo': line['liq'], 'no_mandat': line['mdt'], 'cd_titre_id': line['titre'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'],'cd_article_id': line['art'],
										'cd_paragraphe_id': line['par'],'cd_rubrique_id': line['rub'],'type_procedure': line['proc'],'type_beneficiaire_id': line['typeb'],
										'no_beneficiaire': line['benef'],'obj': line['obj'],'mnt_ord': line['mnt']}))
				self.mandat_ids = result
	
	def receptionner(self):

		for vals in self:
			bord = int(vals.bord_recu)
			val_ex = int(vals.x_exercice_id.id)
			val_struct = int(vals.company_id.id)

			self.env.cr.execute("""UPDATE budg_bordereau_mandatement SET et_doss ='R' WHERE id = %d and x_exercice_id = %d and
			company_id = %d""" %(bord, val_ex, val_struct))

			self.env.cr.execute("select bordmand from budg_compteur_bord_mand_a_viser where x_exercice_id = %d and company_id = %d" % (val_ex, val_struct))
			bordmand = self.env.cr.fetchone()
			no_bord_mandat = bordmand and bordmand[0] or 0
			c1 = int(no_bord_mandat) + 1
			c = str(no_bord_mandat)
			print("la val eng", type(bordmand))
			if c == "0":
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("""INSERT INTO budg_compteur_bord_mand_a_viser(x_exercice_id,company_id,bordmand)  VALUES(%d, %d, %d)""" % (val_ex, val_struct, vals))
			else:
				c1 = int(no_bord_mandat) + 1
				c = str(no_bord_mandat)
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("UPDATE budg_compteur_bord_mand_a_viser SET bordmand = %d  WHERE x_exercice_id = %d and company_id = %d" % (vals, val_ex, val_struct))

			#self.afficher()

			self.write({'et_doss': 'R'})
	
	def envoyer(self):
		
		self.write({'et_doss': 'E'})
		
	
class BudgListeMdt(models.Model):
	_name = "budg_liste_mandatement"
	
	liste_id = fields.Many2one("budg_bordereau_mandatement_controle_a_viser", ondelete='cascade')
	cd_titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one('budg_typeprocedure',string="Type de procédure", readonly= True)
	no_eng = fields.Char(string="N° engagement", readonly= True)
	no_mandat = fields.Many2one("budg_mandat",string="N° Mandat",readonly=True)
	no_lo = fields.Many2one("budg_liqord", string="Liquidation", readonly= True)
	mnt_ord = fields.Integer(string="Montant", readonly= True)
	piecejust_ids = fields.One2many("budg_liste_piece_mdt",'mdt_id')
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date mandat", readonly = True)
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	no_beneficiaire = fields.Char( string ="Bénéficiaire", readonly= True)
	obj = fields.Text(string="Objet", readonly= True)
	envoyer = fields.Selection([('Y','Oui'),('N','Non')], string="Envoyé ?", default='Y')
	modereg = fields.Many2one("ref_modereglement", 'Mode de règlement', readonly=True)
	motif_rejet = fields.Selection([('1','Erreur Montant'),('2','Erreur')],string="Motif rejet")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	state = fields.Selection([
        ('N', 'Nouveau'),
		('V', 'Visé par DCMEF/CG'),
		('R', 'Rejété par DCMEF/CG'),
        ], 'Etat', default='N', index=True, readonly=True, copy=False, track_visibility='always')
	
	
	def viser(self):
		
		mdt = int(self.no_mandat)
		val_ex = int(self.x_exercice_id)
		val_strcut = int(self.company_id)
		for vals in self:
			if self.envoyer == 'Y':
				self.env.cr.execute("""UPDATE budg_mandat SET state ='V', envoyer_daf = 'Y' WHERE id = %d and company_id = %d and
				x_exercice_id = %d""" %(mdt, val_strcut, val_ex))
		
			self.write({'state': 'V'})
	
	def rejeter(self):
		
		mdt = int(self.no_mandat)
		val_ex = int(self.x_exercice_id)
		val_strcut = int(self.company_id)
		
		self.env.cr.execute("""UPDATE budg_mandat SET state ='R' WHERE id = %d and x_exercice_id = %d and
		company_id = %d""" %(mdt, val_ex, val_strcut ))
		
		self.write({'state': 'R'})


	def afficher_piece(self):

		mdt = int(self.no_mandat)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)

		for vals in self:
			vals.env.cr.execute(
				"select lb_long as lib, oblige as obl, ref as re, montant as mnt, dte as dte, nombre as nbr from budg_piece_ord where mandat_id = %d and company_id = %d and x_exercice_id = %d" % (
				mdt, val_struct, val_ex))

			rows = vals.env.cr.dictfetchall()
			result = []

			vals.piecejust_ids.unlink()
			for line in rows:
				result.append((0, 0, {'lib': line['lib'], 'oblige': line['obl'], 'ref': line['re'],'dte': line['dte'], 'mnt': line['mnt'],
									  'nbr': line['nbr']}))
			self.piecejust_ids = result




class BudgListePieceMdt(models.Model):
	_name = "budg_liste_piece_mdt"

	mdt_id = fields.Many2one("budg_liste_mandatement", ondelete='cascade')
	lib = fields.Many2one("budg_typepjbudget", "Libellé", readonly=True)
	oblige = fields.Boolean("Obligatoire", readonly=True)
	ref = fields.Char("Référence", readonly=True)
	dte = fields.Char("Référence", readonly=True)
	nbr = fields.Integer("Nombre", readonly=True)
	mnt = fields.Integer("Montant", readonly=True)


#Renvoi bordereau de mandat DAF / DFC
class BudgBordMdtRenvoiDaf(models.Model):
	_name = "budg_bordereau_mandatement_renvoi_daf"
	_rec_name = "no_bord_mandat"

	name = fields.Char()
	no_bord_mandat = fields.Char("Bord. N°", readonly=True)
	type_bord_trsm = fields.Char('Type de bordereau',default="Bordereau de Transmission de Mandat pour DAF/DFC", readonly=True)
	cd_acteur = fields.Char(string="Acteur", default="DCMEF/CG",readonly=True)
	date_emis = fields.Date(string="Date d'émission", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception", readonly=True)
	num_accuse = fields.Char()
	bord_recu = fields.Many2one("budg_bordereau_mandatement_controle_a_viser", required=True, domain=[('et_doss','=','R')])
	totaux = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",readonly=True)
	cd_acteur_accuse = fields.Char(string="Acteur",  default="DAF/DFC", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	mandat_ids = fields.One2many("budg_liste_mandatement_renvoi", "liste_id")
	et_doss = fields.Selection([
		('N', 'Nouveau'),
		('E', 'Envoyé à la DAF/DFC'),
		('R', 'Receptionné par DAF/DFC'),
	], 'Etat', default='N', required=True)
	total_prec = fields.Integer()
	

	def afficher(self):
		
		id_bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		if self.bord_recu:
		
			for vals in self:
				vals.env.cr.execute("""select m.dt_etat as dte,m.no_lo as liq, m.no_mandat as mdt, m.cd_titre_id as titre, m.cd_section_id as sec, m.cd_chapitre_id as chap,
				m.cd_article_id as art, m.cd_paragraphe_id as par, m.cd_rubrique_id as rub, m.type_procedure as proc, m.type_beneficiaire_id as typeb,
				m.no_beneficiaire as benef, m.obj as obj, m.mnt_ord as mnt from budg_liste_mandatement m
				where  m.liste_id = %d and m.company_id = %d
				and m.x_exercice_id = %d and m.state = 'V' and m.envoyer = 'Y' """ %(id_bord, val_struct, val_ex))
				
				rows = vals.env.cr.dictfetchall()
				result = []
				
				vals.mandat_ids.unlink()
				for line in rows:
					result.append((0,0, {'dt_etat' : line['dte'], 'no_lo': line['liq'], 'no_mandat': line['mdt'], 'cd_titre_id': line['titre'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'],'cd_article_id': line['art'],
										'cd_paragraphe_id': line['par'],'cd_rubrique_id': line['rub'],'type_procedure': line['proc'],'type_beneficiaire_id': line['typeb'],
										'no_beneficiaire': line['benef'],'obj': line['obj'],'mnt_ord': line['mnt']}))
				self.mandat_ids = result
	
	def envoyer(self):

		for vals in self:
			bord = int(vals.bord_recu)
			val_ex = int(vals.x_exercice_id.id)
			val_struct = int(vals.company_id.id)

			self.env.cr.execute("""UPDATE budg_bordereau_mandatement_controle_a_viser SET et_doss ='E' WHERE id = %d and x_exercice_id = %d and
			company_id = %d""" %(bord, val_ex, val_struct))

			self.env.cr.execute("select bordmand from budg_compteur_bord_mand_daf where x_exercice_id = %d and company_id = %d" % (val_ex, val_struct))
			bordmand = self.env.cr.fetchone()
			no_bord_mandat = bordmand and bordmand[0] or 0
			c1 = int(no_bord_mandat) + 1
			c = str(no_bord_mandat)
			print("la val eng", type(bordmand))
			if c == "0":
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("""INSERT INTO budg_compteur_bord_mand_daf(x_exercice_id,company_id,bordmand)  VALUES(%d, %d, %d)""" % (val_ex, val_struct, vals))
			else:
				c1 = int(no_bord_mandat) + 1
				c = str(no_bord_mandat)
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("UPDATE budg_compteur_bord_mand_daf SET bordmand = %d  WHERE x_exercice_id = %d and company_id = %d" % (vals, val_ex, val_struct))

			#self.afficher()

			self.write({'et_doss': 'E'})
	

	
class BudgListeMdtRenvoi(models.Model):
	_name = "budg_liste_mandatement_renvoi"
	
	liste_id = fields.Many2one("budg_bordereau_mandatement_renvoi_daf", ondelete='cascade')
	cd_titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one('budg_typeprocedure',string="Type de procédure", readonly= True)
	no_eng = fields.Char(string="N° engagement", readonly= True)
	no_mandat = fields.Many2one("budg_mandat",string="N° Mandat",readonly=True)
	no_lo = fields.Many2one("budg_liqord", string="Liquidation", readonly= True)
	mnt_ord = fields.Integer(string="Montant", readonly= True)
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date mandat", readonly = True)
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	no_beneficiaire = fields.Char( string ="Bénéficiaire", readonly= True)
	obj = fields.Text(string="Objet", readonly= True)
	envoyer = fields.Selection([('Y','Oui'),('N','Non')], string="Envoyer ?", default='Y')
	modereg = fields.Many2one("ref_modereglement", 'Mode de règlement', readonly=True)
	motif_rejet = fields.Selection([('1','Erreur Montant'),('2','Erreur')],string="Motif rejet")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	state = fields.Selection([
        ('N', 'Nouveau'),
		('V', 'Visé par DCMEF/CG'),
		('R', 'Rejété par DCMEF/CG'),
        ], 'Etat', default='V', index=True, readonly=True, copy=False, track_visibility='always')
	


#Reception bordereau envoyer par dcmef/cg
class BudgBordMdtRecepDcmef(models.Model):
	_name = "budg_bordereau_mandatement_recep_dcmef"
	_rec_name = "no_bord_mandat"

	name = fields.Char()
	no_bord_mandat = fields.Char("Bord. N°", readonly=True)
	type_bord_trsm = fields.Char('Type de bordereau',default="Bordereau de Transmisson de prise en charge", readonly=True)
	cd_acteur = fields.Char(string="Acteur", default="DCMEF/CG",readonly=True)
	date_emis = fields.Date(string="Date d'émission", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception", readonly=True)
	num_accuse = fields.Char()
	bord_recu = fields.Many2one("budg_bordereau_mandatement_renvoi_daf", required=True, domain=[('et_doss','=','E')])
	totaux = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",readonly=True)
	cd_acteur_accuse = fields.Char(string="Acteur",  default="DAF/DFC", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	mandat_ids = fields.One2many("budg_liste_mandatement_renvoi", "liste_id")
	et_doss = fields.Selection([
		('N', 'Nouveau'),
		('E', 'Envoyé par DCMEF/CG'),
		('R', 'Réceptionné'),
		('PC', 'Envoyé pour PC'),
		('RP','Réceptionné pour PC')
	], 'Etat', default='E', required=True)
	total_prec = fields.Integer()
	

	def afficher(self):
		
		id_bord = int(self.bord_recu)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		if self.bord_recu:
		
			for vals in self:
				vals.env.cr.execute("""select m.dt_etat as dte,m.no_lo as liq, m.no_mandat as mdt, m.cd_titre_id as titre, m.cd_section_id as sec, m.cd_chapitre_id as chap,
				m.cd_article_id as art, m.cd_paragraphe_id as par, m.cd_rubrique_id as rub, m.type_procedure as proc, m.type_beneficiaire_id as typeb,
				m.no_beneficiaire as benef, m.obj as obj, m.mnt_ord as mnt from budg_liste_mandatement_renvoi m
				where  m.liste_id = %d and m.company_id = %d
				and m.x_exercice_id = %d and m.state = 'V' and m.envoyer = 'Y' """ %(id_bord, val_struct, val_ex))
				
				rows = vals.env.cr.dictfetchall()
				result = []
				
				vals.mandat_ids.unlink()
				for line in rows:
					result.append((0,0, {'dt_etat' : line['dte'], 'no_lo': line['liq'], 'no_mandat': line['mdt'], 'cd_titre_id': line['titre'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'],'cd_article_id': line['art'],
										'cd_paragraphe_id': line['par'],'cd_rubrique_id': line['rub'],'type_procedure': line['proc'],'type_beneficiaire_id': line['typeb'],
										'no_beneficiaire': line['benef'],'obj': line['obj'],'mnt_ord': line['mnt']}))
				self.mandat_ids = result
	
	def receptionner(self):

		for vals in self:
			bord = int(vals.bord_recu)
			val_ex = int(vals.x_exercice_id.id)
			val_struct = int(vals.company_id.id)

			self.env.cr.execute("""UPDATE budg_bordereau_mandatement_renvoi_daf SET et_doss ='R' WHERE id = %d and x_exercice_id = %d and
			company_id = %d""" %(bord, val_ex, val_struct))

			self.env.cr.execute("select bordmand from budg_compteur_bord_mand_cf where x_exercice_id = %d and company_id = %d" % (val_ex, val_struct))
			bordmand = self.env.cr.fetchone()
			no_bord_mandat = bordmand and bordmand[0] or 0
			c1 = int(no_bord_mandat) + 1
			c = str(no_bord_mandat)
			print("la val eng", type(bordmand))
			if c == "0":
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("""INSERT INTO budg_compteur_bord_mand_cf(x_exercice_id,company_id,bordmand)  VALUES(%d, %d, %d)""" % (val_ex, val_struct, vals))
			else:
				c1 = int(no_bord_mandat) + 1
				c = str(no_bord_mandat)
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("UPDATE budg_compteur_bord_mand_cf SET bordmand = %d  WHERE x_exercice_id = %d and company_id = %d" % (vals, val_ex, val_struct))

			#self.afficher()

			self.write({'et_doss': 'R'})
	
	def envoyer(self):
		
		self.write({'et_doss': 'PC'})
	

	
class BudgListeMdtRecep(models.Model):
	_name = "budg_liste_mandatement_recep"
	
	liste_id = fields.Many2one("budg_bordereau_mandatement_recep_dcmef", ondelete='cascade')
	cd_titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one('budg_typeprocedure',string="Type de procédure", readonly= True)
	no_eng = fields.Char(string="N° engagement", readonly= True)
	no_mandat = fields.Many2one("budg_mandat",string="N° Mandat",readonly=True)
	no_lo = fields.Many2one("budg_liqord", string="Liquidation", readonly= True)
	mnt_ord = fields.Integer(string="Montant", readonly= True)
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date mandat", readonly = True)
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	no_beneficiaire = fields.Char( string ="Bénéficiaire", readonly= True)
	obj = fields.Text(string="Objet", readonly= True)
	envoyer = fields.Boolean("Envoyer ?")
	modereg = fields.Many2one("ref_modereglement", 'Mode de règlement', readonly=True)
	motif_rejet = fields.Selection([('1','Erreur Montant'),('2','Erreur')],string="Motif rejet")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	state = fields.Selection([
        ('N', 'Nouveau'),
		('V', 'Visé par DCMEF/CG'),
		('R', 'Rejété par DCMEF/CG'),
        ], 'Etat', default='N', index=True, readonly=True, copy=False, track_visibility='always')



class BudgBordMdtControleRejet(models.Model):
	_name = "budg_bordereau_mandatement_controle_rejet"
	_rec_name = "no_bord_mandat"

	name = fields.Char()
	no_bord_mandat = fields.Char("Bord. N°", readonly=True)
	type_bord_trsm = fields.Char('Type de bordereau', readonly=True)
	cd_acteur = fields.Char(string="Acteur", readonly=True)
	date_emis = fields.Date(string="Date d'émission", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception", readonly=True)
	num_accuse = fields.Char()
	totaux = fields.Integer()
	text_amount = fields.Char(string="Montant en lettre", required=False, compute="amount_to_words")
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",readonly=True)
	cd_acteur_accuse = fields.Char(string="Acteur", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	mandat_ids = fields.Many2many("budg_mandat", "budg_detail_bord_mandat_rejet", domain=[('state','=','O')], string="Liste des mandats")
	et_doss = fields.Selection([
		('N', 'Nouveau'),
		('E', 'Envoyé à la DAF/DFC '),
	], 'Etat', default='N', required=True)
	total_prec = fields.Integer()



class BudgBordMdtControle(models.Model):
	_name = "budg_bordereau_mandatement_controle_viser"
	_rec_name = "no_bord_mandat"

	name = fields.Char()
	no_bord_mandat = fields.Char("Bord. N°", readonly=True)
	type_bord_trsm = fields.Char('Type de bordereau',default="Bordereau de Reception Prise en Charge", readonly=True)
	cd_acteur = fields.Char(string="Acteur", default='DAF/DFC',  readonly=True)
	bord_recu = fields.Many2one("budg_bordereau_mandatement_recep_dcmef",required=True,domain=[('et_doss','=','PC')])
	date_emis = fields.Date(string="Date d'émission", default=fields.Date.context_today, readonly=True)
	date_recus = fields.Date("Date de reception",default=fields.Date.context_today, readonly=True)
	num_accuse = fields.Char()
	totaux = fields.Integer()
	company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Company Currency",readonly=True)
	cd_acteur_accuse = fields.Char(string="Acteur", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, string="Structure")
	mandat_ids = fields.One2many("budg_liste_mandatement_pc", "liste_id", string="Liste des mandats")
	et_doss = fields.Selection([
		('N', 'Nouveau'),
		('T', 'Envoyé pour prise en charge'),
		('PC', 'Réceptionné pour prise en charge'),
        ], 'Etat', default='T', required=True)
	total_prec = fields.Integer()


	def receptionner(self):
		for vals in self:
			#bord = int(self.bord_recu)
			val_ex = int(vals.x_exercice_id.id)
			val_struct = int(vals.company_id.id)

			self.env.cr.execute("""UPDATE budg_bordereau_mandatement_recep_dcmef SET et_doss ='RP' WHERE id = %d and x_exercice_id = %d and
			company_id = %d""" %(bord, val_ex, val_strcut))


			vals.env.cr.execute("select bordmand from budg_compteur_bord_mand_viser where x_exercice_id = %d and company_id = %d" %(val_ex, val_struct))
			bordmand = self.env.cr.fetchone()
			no_bord_mandat = bordmand and bordmand[0] or 0
			c1 = int(no_bord_mandat) + 1
			c = str(no_bord_mandat)
			print("la val eng", type(bordmand))
			if c == "0":
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("""INSERT INTO budg_compteur_bord_mand_viser(x_exercice_id,company_id,bordmand)  VALUES(%d, %d, %d)""" % (val_ex, val_struct, vals))
			else:
				c1 = int(no_bord_mandat) + 1
				c = str(no_bord_mandat)
				ok = str(c1).zfill(4)
				self.no_bord_mandat = ok
				vals = c1
				self.env.cr.execute("UPDATE budg_compteur_bord_mand_viser SET bordmand = %d  WHERE x_exercice_id = %d and company_id = %d" % (vals, val_ex, val_struct))


			#self.afficher()

			self.write({'et_doss': 'PC'})
	
	def envoyer(self):
		
		self.write({'et_doss': 'T'})
	


	def afficher(self):
		
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		for vals in self:
			vals.env.cr.execute("""select distinct m.id as mdt, m.dt_etat as dte,m.no_lo as liq, m.cd_titre_id as titre, m.cd_section_id as sec, m.cd_chapitre_id as chap,
			m.cd_article_id as art, m.cd_paragraphe_id as par, m.cd_rubrique_id as rub, m.type_procedure as proc, m.type_beneficiaire_id as typeb,
			m.no_beneficiaire as benef, m.obj as obj, m.mnt_ord as mnt from budg_mandat m
			where m.company_id = %d and m.x_exercice_id = %d and m.state = 'V' and m.envoyer_daf = 'Y' """ %(val_struct, val_ex))
			
			rows = vals.env.cr.dictfetchall()
			result = []
			
			vals.mandat_ids.unlink()
			for line in rows:
				result.append((0,0, {'dt_etat' : line['dte'], 'no_lo': line['liq'], 'no_mandat': line['mdt'], 'cd_titre_id': line['titre'], 'cd_section_id': line['sec'], 'cd_chapitre_id': line['chap'],'cd_article_id': line['art'],
									'cd_paragraphe_id': line['par'],'cd_rubrique_id': line['rub'],'type_procedure': line['proc'],'type_beneficiaire_id': line['typeb'],
									'no_beneficiaire': line['benef'],'obj': line['obj'],'mnt_ord': line['mnt']}))
			self.mandat_ids = result


class BudgListeMdtPc(models.Model):
	_name = "budg_liste_mandatement_pc"
	
	liste_id = fields.Many2one("budg_bordereau_mandatement_controle_viser", ondelete='cascade')
	cd_titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	cd_section_id = fields.Many2one("budg_section",string = "Section", readonly=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", string = "Chapitre", readonly=True)
	cd_article_id = fields.Many2one("budg_param_article", string = "Article", readonly=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", string = "Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", string = "Rubrique", readonly=True)
	type_procedure = fields.Many2one('budg_typeprocedure',string="Type de procédure", readonly= True)
	no_eng = fields.Char(string="N° engagement", readonly= True)
	no_mandat = fields.Many2one("budg_mandat",string="N° Mandat",readonly=True)
	no_lo = fields.Many2one("budg_liqord", string="Liquidation", readonly= True)
	mnt_ord = fields.Integer(string="Montant", readonly= True)
	dt_etat = fields.Date(default=fields.Date.context_today, string="Date mandat", readonly = True)
	type_beneficiaire_id = fields.Many2one("ref_typebeneficiaire", readonly=True, string = "Catégorie")
	no_beneficiaire = fields.Char( string ="Identité", readonly= True)
	obj = fields.Text(string="Objet", readonly= True)
	modereg = fields.Many2one("ref_modereglement", 'Mode de règlement', readonly=True)
	motif_rejet = fields.Selection([('1','Erreur Montant'),('2','Erreur')],string="Motif rejet")
	x_exercice_id = fields.Many2one("ref_exercice", default=lambda self: self.env['ref_exercice'].search([('etat','=', 1)]), string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	state = fields.Selection([
        ('N', 'Nouveau'),
		('I', 'Pris en charge'),
		('J', 'Rejéter'),
        ], 'Etat', default='N', index=True, readonly=True, copy=False, track_visibility='always')
	
	def PrendreEnCharge(self):
		
		mdt = int(self.no_mandat)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		self.env.cr.execute("""UPDATE budg_mandat SET state ='I' WHERE id = %d and company_id = %d and
		x_exercice_id = %d""" %(mdt, val_struct, val_ex))
		
		self.write({'state': 'I'})
	
	def rejeter(self):
		
		mdt = int(self.no_mandat)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)
		
		self.env.cr.execute("""UPDATE budg_mandat SET state ='J' WHERE id = %d and x_exercice_id = %d and
		company_id = %d""" %(mdt, val_ex, val_struct ))
		
		self.write({'state': 'J'})


class Budg_Compteur_bord_mandPc(models.Model):
	_name = "budg_compteur_bord_mand_pc"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordmand = fields.Integer(default=0)


class Budg_Compteur_bordMandAViser(models.Model):
	_name = "budg_compteur_bord_mand_a_viser"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordmand = fields.Integer(default=0)
 ###
class Budg_CompteurBordEngCtrl(models.Model):
	_name = "budg_compteur_bord_eng_ctrl"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordeng = fields.Integer(default=0)

class Budg_CompteurBordEngRecep(models.Model):
	_name = "budg_compteur_bord_eng_recep"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordeng = fields.Integer(default=0)

class Budg_CompteurBordEngRenvoi(models.Model):
	_name = "budg_compteur_bord_eng_renvoi"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordeng = fields.Integer(default=0)
	
class Budg_Compteur_bord_mandViser(models.Model):
	_name = "budg_compteur_bord_mand_viser"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordmand = fields.Integer(default=0)

class Budg_Compteur_bordMandDaf(models.Model):
	_name = "budg_compteur_bord_mand_daf"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordmand = fields.Integer(default=0)
	
class Budg_Compteur_bordMandCf(models.Model):
	_name = "budg_compteur_bord_mand_cf"

	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	bordmand = fields.Integer(default=0)




class BudgAnnulationEngagement(models.Model):
	_name = "budg_annulation_engagement"
	_rec_name = "eng_id"
	
	eng_id = fields.Many2one("budg_engagement", "N° Engagement",required=True,domain=['|',('state','=','V'),('state','=','C')])
	titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	section_id = fields.Many2one("budg_section", "Section", readonly=True)
	chapitre_id = fields.Many2one("budg_chapitre", "Chapitre", readonly=True)
	article_id = fields.Many2one("budg_param_article", "Article", readonly=True)
	para_id = fields.Many2one("budg_paragraphe", "Article", readonly=True)
	rub_id = fields.Many2one("budg_rubrique", "Rubrique", readonly=True)
	mnt = fields.Float("Montant", readonly=True)
	objet = fields.Text("Objet", readonly=True)
	beneficiaire = fields.Many2one("ref_beneficiaire", "Bénéficiaire", readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	state = fields.Selection([('V','Approuvé'),('A','Annulé')],default='V', string="Etat", required=True)
	
	
	#Récuperer les elements de l'engagement choisi
	@api.onchange("eng_id")
	def Valeur(self):
		for vals in self:
			if vals.eng_id:
				self.titre_id = self.eng_id.cd_titre_id
				self.section_id = self.eng_id.cd_section_id
				self.chapitre_id = self.eng_id.cd_chapitre_id
				self.article_id = self.eng_id.cd_article_id
				self.para_id = self.eng_id.cd_paragraphe_id
				self.rub_id = self.eng_id.cd_rubrique_id
				self.mnt = self.eng_id.mnt_eng
				self.beneficiaire = self.eng_id.no_beneficiaire
				self.objet = self.eng_id.lb_obj

	#Annulation Engagement et restauration du crédit
	def AnnulerEngagement(self):
		
		for val in self:
			eng = int(val.eng_id)
			tit = int(val.titre_id)
			sec = int(val.section_id)
			chap = int(val.chapitre_id)
			art = int(val.article_id)
			par = int(val.para_id)
			rub = int(val.rub_id)
			no_ex = int(val.x_exercice_id)
			struct = int(val.company_id)
			mnt = int(val.mnt)
		
			self.env.cr.execute("""UPDATE budg_ligne_exe_dep SET mnt_disponible = mnt_disponible + %d
			WHERE cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and 
			cd_art_id = %d and cd_paragraphe_id = %d and cd_rubrique_id = %d and company_id = %d and x_exercice_id = %d""" %(mnt, tit, sec, chap, art, par, rub, struct, no_ex))
			
			self.env.cr.execute("""UPDATE budg_engagement SET state = 'A' WHERE id = %d and x_exercice_id = %d and company_id = %d""" %(eng, no_ex, struct))
			
			self.write({'state': 'A'})
	

class BudgCorrectionEngagementApprobation(models.Model):
	_name = "budg_correction_engagement_approbation"
	_rec_name = "eng_id"
	
	eng_id = fields.Many2one("budg_engagement", "N° Engagement",required=True)
	titre_id = fields.Many2one("budg_titre", "Titre", readonly=True)
	section_id = fields.Many2one("budg_section", "Section", readonly=True)
	chapitre_id = fields.Many2one("budg_chapitre", "Chapitre", readonly=True)
	article_id = fields.Many2one("budg_param_article", "Article", readonly=True)
	para_id = fields.Many2one("budg_paragraphe", "Article", readonly=True)
	rub_id = fields.Many2one("budg_rubrique", "Rubrique", readonly=True)
	mnt = fields.Float("Montant", readonly=True)
	objet = fields.Text("Objet", readonly=False)
	beneficiaire = fields.Many2one("ref_beneficiaire", "Bénéficiaire", readonly=False)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	state = fields.Selection([('V','Approuvé'),('C','Corrigé')],default='V', string="Etat", required=True)


	#Récuperer les elements de l'engagement choisi
	@api.onchange("eng_id")
	def Valeur(self):
		for vals in self:
			if vals.eng_id:
				self.titre_id = self.eng_id.cd_titre_id
				self.section_id = self.eng_id.cd_section_id
				self.chapitre_id = self.eng_id.cd_chapitre_id
				self.article_id = self.eng_id.cd_article_id
				self.para_id = self.eng_id.cd_paragraphe_id
				self.rub_id = self.eng_id.cd_rubrique_id
				self.mnt = self.eng_id.mnt_eng
				self.beneficiaire = self.eng_id.no_beneficiaire
				self.objet = self.eng_id.lb_obj
	
	#Correction de l'engagement
	def corriger(self):
		for val in self:
			benef = int(val.beneficiaire)
			benefe = val.beneficiaire.nm
			obj = str(val.objet)
			eng = int(self.eng_id)
			enge = self.eng_id.no_eng
			no_ex = int(val.x_exercice_id)
			struct = int(val.company_id)
			
			if self.beneficiaire:
				self.env.cr.execute("""UPDATE budg_engagement SET no_beneficiaire = %d WHERE id = %d and x_exercice_id = %d and company_id = %d""" %(benef, eng, no_ex, struct))
				self.env.cr.execute("""UPDATE budg_liqord SET no_beneficiaire = %s WHERE no_eng = %s and x_exercice_id = %s and company_id = %s""" ,(benefe, eng, no_ex, struct))
				self.env.cr.execute("""UPDATE budg_mandat SET no_beneficiaire = %s WHERE no_eng = %s and x_exercice_id = %s and company_id = %s""" ,(benefe, enge, no_ex, struct))

				self.write({'state': 'C'})

			elif self.objet:
				self.env.cr.execute("""UPDATE budg_engagement SET lb_obj = %s WHERE id = %s and x_exercice_id = %s and company_id = %s""" ,(obj, eng, no_ex, struct))
				self.env.cr.execute("""UPDATE budg_liqord SET lb_obj = %s WHERE no_eng = %s and x_exercice_id = %s and company_id = %s""" ,(obj, eng, no_ex, struct))
				self.env.cr.execute("""UPDATE budg_mandat SET obj = %s WHERE no_eng = %s and x_exercice_id = %s and company_id = %s""" ,(obj, enge, no_ex, struct))

				self.write({'state': 'C'})
			else:
				raise ValidationError(_("Pas de données à corriger."))


class BudgSignataire(models.Model):
	_name = "budg_signataire"

	code = fields.Char("Code", required=True, size=4)
	name = fields.Many2one("res.users", string="Signataire", required=True)
	distinction = fields.Char("Distinction Honorifique")
	active = fields.Boolean("Actif", default=True)


class BudgEditionExeDep(models.Model):
	_name = "budg_execution_depense"

	name = fields.Char("titre", default="Situation exécutoire des dépenses")
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	depense_line = fields.One2many("budg_execution_depense_lines","depense_id", readonly=True)

	def afficher(self):

		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)

		for vals in self:
			vals.env.cr.execute("""select * from budg_ligne_exe_dep l where l.company_id = %d and l.x_exercice_id = %d
			 order by l.cd_titre_id, l.cd_section_id, l.cd_chapitre_id, l.cd_art_id, l.cd_paragraphe_id, l.cd_rubrique_id
			  """ % (val_struct, val_ex))

			rows = vals.env.cr.dictfetchall()
			result = []

			vals.depense_line.unlink()
			for line in rows:
				result.append((0, 0, {'titre': line['cd_titre_id'], 'section': line['cd_section_id'],
									  'chapitre': line['cd_chapitre_id'], 'article': line['cd_art_id'],
									  'paragraphe': line['cd_paragraphe_id'], 'rubrique': line['cd_rubrique_id'],
									  'initiale': line['mnt_budgetise'], 'corrige': line['mnt_corrige'],
									  'engagement': line['mnt_engage'], 'dispo': line['mnt_disponible'], 'mandat': line['mnt_mandate'], 'taux': line['taux'], 'reste': line['reste_mandat']}))
			self.depense_line = result



class BudgEditionExeDepLine(models.Model):
	_name = "budg_execution_depense_lines"

	depense_id = fields.Many2one("budg_execution_depense", ondelete='cascade')
	titre = fields.Many2one("budg_titre", "Titre")
	section = fields.Many2one("budg_section", "Section")
	chapitre = fields.Many2one("budg_chapitre", "Chapitre")
	article = fields.Many2one("budg_param_article", "Article")
	paragraphe = fields.Many2one("budg_paragraphe", "Paragraphe")
	rubrique = fields.Many2one("budg_rubrique", "Rubrique")
	initiale = fields.Float("Dotation initiale")
	corrige = fields.Float("Dotation corrigée")
	engagement = fields.Float("Engagement")
	dispo = fields.Float("Disponible")
	mandat = fields.Float("Mandatement")
	taux = fields.Float("Taux de réalisation(%)",digits = (15,2))
	reste = fields.Float("Reste à mandater")



class BudgEditionExeRec(models.Model):
	_name = "budg_execution_recette"

	name = fields.Char("titre", default="Situation exécutoire des recettes")
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	recette_line = fields.One2many("budg_execution_rec_lines","recette_id", readonly=True)

	def afficher(self):

		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)

		for vals in self:
			vals.env.cr.execute("""select * from budg_ligne_exe_rec l where l.company_id = %d and l.x_exercice_id = %d
			 order by l.cd_titre_id, l.cd_section_id, l.cd_chapitre_id, l.cd_art_id, l.cd_paragraphe_id, l.cd_rubrique_id
			  """ % (val_struct, val_ex))

			rows = vals.env.cr.dictfetchall()
			result = []

			vals.recette_line.unlink()
			for line in rows:
				result.append((0, 0, {'titre': line['cd_titre_id'], 'section': line['cd_section_id'],
									  'chapitre': line['cd_chapitre_id'], 'article': line['cd_art_id'],
									  'paragraphe': line['cd_paragraphe_id'], 'rubrique': line['cd_rubrique_id'],
									  'initiale': line['mnt_budgetise'], 'corrige': line['mnt_corrige'],
									  'emis': line['mnt_rec'], 'taux': line['taux'], 'reste': line['reste_emettre']}))
			self.recette_line = result



class BudgEditionExeRecLine(models.Model):
	_name = "budg_execution_rec_lines"

	recette_id = fields.Many2one("budg_execution_recette", ondelete='cascade')
	titre = fields.Many2one("budg_titre", "Titre")
	section = fields.Many2one("budg_section", "Section")
	chapitre = fields.Many2one("budg_chapitre", "Chapitre")
	article = fields.Many2one("budg_param_article", "Article")
	paragraphe = fields.Many2one("budg_paragraphe", "Paragraphe")
	rubrique = fields.Many2one("budg_rubrique", "Rubrique")
	initiale = fields.Float("Dotation initiale")
	corrige = fields.Float("Dotation corrigée")
	emis = fields.Float("Titre émis")
	taux = fields.Float("Taux de réalisation(%)",digits = (15,2))
	reste = fields.Float("Reste à recouvrer")


class BudgConsulEng(models.Model):
	_name = "budg_consul_eng"

	name = fields.Char("Name", default="Liste des engagements")
	dte_deb = fields.Date("Date debut")
	dte_fin = fields.Date("Date fin")
	procedure_id = fields.Many2one("budg_typeprocedure","Type de procédure")
	etat = fields.Selection([
		('N', 'Confirmé'),
		('V', 'Approuvé'),
		('A','Annulé'),
		('W', 'Visé'),
		('R','Réjeté'),
		('LC','Liquidation en cours'),
		('L','Liquidé'),
		('T','Tous'),
	], string = "Etat")
	x_exercice_id = fields.Many2one("ref_exercice",
									default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice", readonly=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	engagement_line = fields.One2many("budg_consul_engagement_lines", "eng_id", readonly=True)

	def afficher(self):

		dte_deb = self.dte_deb
		dte_fin = self.dte_fin
		v_etat = self.etat
		v_proc = int(self.procedure_id)
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)


		for vals in self:
			vals.env.cr.execute("""select e.dt_etat as dte, e.no_eng as eng, e.cd_rubrique_id as rub,
			e.no_beneficiaire as benef, e.lb_obj as obj, e.mnt_eng as mnt from budg_engagement e 
			where e.company_id = %d and e.x_exercice_id = %d order by e.no_eng """ % (val_struct, val_ex))

			rows = vals.env.cr.dictfetchall()
			result = []

			vals.engagement_line.unlink()
			for line in rows:
				result.append((0, 0, {'dte': line['dte'], 'no_eng': line['eng'], 'rubrique_id': line['rub'],
									  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
			self.engagement_line = result

		if dte_deb and dte_fin:
			for vals in self:
				vals.env.cr.execute("""select e.dt_etat as dte, e.no_eng as eng, e.cd_rubrique_id as rub,
				e.no_beneficiaire as benef, e.lb_obj as obj, e.mnt_eng as mnt from budg_engagement e 
				where e.company_id = %s and e.x_exercice_id = %s and e.dt_etat between '%s' and '%s' order by e.no_eng """ % (val_struct, val_ex, dte_deb, dte_fin))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.engagement_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_eng': line['eng'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
				self.engagement_line = result

		elif dte_deb and dte_fin and v_etat:
			for vals in self:
				vals.env.cr.execute("""select e.dt_etat as dte, e.no_eng as eng, e.cd_rubrique_id as rub,
				e.no_beneficiaire as benef, e.lb_obj as obj, e.mnt_eng as mnt from budg_engagement e 
				where e.company_id = %s and e.x_exercice_id = %s and e.state = '%s' e.dt_etat between '%s' and '%s' order by e.no_eng """ % (val_struct, val_ex, v_etat, dte_deb, dte_fin))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.engagement_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_eng': line['eng'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
				self.engagement_line = result

		elif dte_deb and dte_fin and v_etat and v_proc:
			for vals in self:
				vals.env.cr.execute("""select e.dt_etat as dte, e.no_eng as eng, e.cd_rubrique_id as rub,
				e.no_beneficiaire as benef, e.lb_obj as obj, e.mnt_eng as mnt from budg_engagement e 
				where e.company_id = %s and e.x_exercice_id = %s and e.state = '%s' e.dt_etat between '%s' and '%s' and type_procedure = %s order by e.no_eng """ % (val_struct, val_ex, v_etat, dte_deb, dte_fin, v_proc))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.engagement_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_eng': line['eng'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
				self.engagement_line = result

		elif v_etat:
			for vals in self:
				vals.env.cr.execute("""select e.dt_etat as dte, e.no_eng as eng, e.cd_rubrique_id as rub,
				e.no_beneficiaire as benef, e.lb_obj as obj, e.mnt_eng as mnt from budg_engagement e 
				where e.company_id = %s and e.x_exercice_id = %s and e.state = '%s' order by e.no_eng """ % (val_struct, val_ex, v_etat))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.engagement_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_eng': line['eng'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
				self.engagement_line = result

		elif v_etat and v_proc:
			for vals in self:
				vals.env.cr.execute("""select e.dt_etat as dte, e.no_eng as eng, e.cd_rubrique_id as rub,
				e.no_beneficiaire as benef, e.lb_obj as obj, e.mnt_eng as mnt from budg_engagement e 
				where e.company_id = %s and e.x_exercice_id = %s and e.state = '%s' and type_procedure = %s order by e.no_eng """ % (val_struct, val_ex, v_etat, v_proc))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.engagement_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_eng': line['eng'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
				self.engagement_line = result

		elif dte_deb and dte_fin and v_proc:
			for vals in self:
				vals.env.cr.execute("""select e.dt_etat as dte, e.no_eng as eng, e.cd_rubrique_id as rub,
				e.no_beneficiaire as benef, e.lb_obj as obj, e.mnt_eng as mnt from budg_engagement e 
				where e.company_id = %s and e.x_exercice_id = %s and e.dt_etat between '%s' and '%s' and type_procedure = %s order by e.no_eng """ % (val_struct, val_ex, dte_deb, dte_fin, v_proc))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.engagement_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_eng': line['eng'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
				self.engagement_line = result





class BudgConsulEngLine(models.Model):
	_name = "budg_consul_engagement_lines"


	eng_id = fields.Many2one("budg_consul_eng", ondelete='cascade')
	dte = fields.Date("Date")
	no_eng = fields.Char("N° Eng")
	objet = fields.Text("Objet")
	rubrique_id = fields.Many2one("budg_rubrique","Rubrique")
	montant = fields.Integer("Montant")
	beneficiaire_id = fields.Many2one("ref_beneficiaire","Bénéficiaire")



class BudgConsulLiq(models.Model):
	_name = "budg_consul_liq"

	name = fields.Char("Name", default="Liste des liquidations")
	dte_deb = fields.Date("Date debut")
	dte_fin = fields.Date("Date fin")
	etat = fields.Selection([
		('N', 'Confirmé'),
		('L','Certifié'),
		('A','Annulé'),
		('T','Tous'),
	], string = "Etat")
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice", readonly=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	liquidation_line = fields.One2many("budg_consul_liquidation_lines", "liq_id", readonly=True)


	def afficher(self):

		dte_deb = self.dte_deb
		dte_fin = self.dte_fin
		v_etat = self.etat
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)

		for vals in self:
			vals.env.cr.execute("""select l.dt_etat as dte, l.no_lo as liq, l.cd_rubrique_id as rub,
			l.no_beneficiaire as benef, l.lb_obj as obj, l.mnt_eng as mnt from budg_liqord l
			where l.company_id = %d and l.x_exercice_id = %d order by l.no_lo """ % (val_struct, val_ex))

			rows = vals.env.cr.dictfetchall()
			result = []

			vals.liquidation_line.unlink()
			for line in rows:
				result.append((0, 0, {'dte': line['dte'], 'no_liq': line['liq'], 'rubrique_id': line['rub'],
									  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
			self.liquidation_line = result

		if dte_deb and dte_fin:
			for vals in self:
				vals.env.cr.execute("""select l.dt_etat as dte, l.no_lo as liq, l.cd_rubrique_id as rub,
				l.no_beneficiaire as benef, l.lb_obj as obj, l.mnt_paye as mnt from budg_liqord l 
				where l.company_id = %s and l.x_exercice_id = %s and l.dt_etat between '%s' and '%s' order by l.no_lo """ % (
				val_struct, val_ex, dte_deb, dte_fin))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.liquidation_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_liq': line['liq'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'],
										  'montant': line['mnt']}))
				self.liquidation_line = result

			if v_etat:
				for vals in self:
					vals.env.cr.execute("""select l.dt_etat as dte, l.no_lo as liq, l.cd_rubrique_id as rub,
					l.no_beneficiaire as benef, l.lb_obj as obj, l.mnt_paye as mnt from budg_liqord l
					where l.company_id = %s and l.x_exercice_id = %s and l.state = '%s' and l.dt_etat between '%s' and '%s' order by l.no_lo """ % (
					val_struct, val_ex, v_etat, dte_deb, dte_fin))

					rows = vals.env.cr.dictfetchall()
					result = []

					vals.liquidation_line.unlink()
					for line in rows:
						result.append((0, 0, {'dte': line['dte'], 'no_liq': line['liq'], 'rubrique_id': line['rub'],
											  'beneficiaire_id': line['benef'], 'objet': line['obj'],
											  'montant': line['mnt']}))
					self.liquidation_line = result

		elif v_etat:
			for vals in self:
				vals.env.cr.execute("""select l.dt_etat as dte, l.no_lo as liq, l.cd_rubrique_id as rub,
				l.no_beneficiaire as benef, l.lb_obj as obj, l.mnt_paye as mnt from budg_liqord l
				where l.company_id = %s and l.x_exercice_id = %s and l.state = '%s' order by l.no_lo """ % (
				val_struct, val_ex, v_etat))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.liquidation_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_liq': line['liq'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'],
										  'montant': line['mnt']}))
				self.liquidation_line = result


class BudgConsulLiqLine(models.Model):
	_name = "budg_consul_liquidation_lines"

	liq_id = fields.Many2one("budg_consul_liq", ondelete='cascade')
	dte = fields.Date("Date")
	no_liq = fields.Char("N° Liq")
	objet = fields.Text("Objet")
	rubrique_id = fields.Many2one("budg_rubrique","Rubrique")
	montant = fields.Integer("Montant")
	beneficiaire_id = fields.Char("Bénéficiaire")



class BudgConsulMdt(models.Model):
	_name = "budg_consul_mdt"

	name = fields.Char("Name", default="Liste des mandats")
	dte_deb = fields.Date("Date debut")
	dte_fin = fields.Date("Date fin")
	etat = fields.Selection([
		('N', 'Confirmé'),
		('O','Ordonnancé'),
		('E','Pris en charge'),
		('T','Tous'),
	], string = "Etat")
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice", readonly=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	mandat_line = fields.One2many("budg_consul_mandat_lines", "mdt_id", readonly=True)


	def afficher(self):

		dte_deb = self.dte_deb
		dte_fin = self.dte_fin
		v_etat = self.etat
		val_ex = int(self.x_exercice_id)
		val_struct = int(self.company_id)

		for vals in self:
			vals.env.cr.execute("""select m.dt_etat as dte, m.no_mandat as mdt, m.cd_rubrique_id as rub,
			m.no_beneficiaire as benef, m.obj as obj, m.mnt_ord as mnt from budg_mandat m
			where m.company_id = %d and m.x_exercice_id = %d order by m.no_mandat """ % (val_struct, val_ex))

			rows = vals.env.cr.dictfetchall()
			result = []

			vals.mandat_line.unlink()
			for line in rows:
				result.append((0, 0, {'dte': line['dte'], 'no_mdt': line['mdt'], 'rubrique_id': line['rub'],
									  'beneficiaire_id': line['benef'], 'objet': line['obj'], 'montant': line['mnt']}))
			self.mandat_line = result

		if dte_deb and dte_fin:
			for vals in self:
				vals.env.cr.execute("""select m.dt_etat as dte, m.no_mandat as mdt, m.cd_rubrique_id as rub,
				m.no_beneficiaire as benef, m.obj as obj, m.mnt_ord as mnt from budg_mandat m 
				where m.company_id = %s and m.x_exercice_id = %s and m.dt_etat between '%s' and '%s' order by m.no_mandat """ % (
				val_struct, val_ex, dte_deb, dte_fin))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.mandat_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_mandat': line['mdt'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'],
										  'montant': line['mnt']}))
				self.mandat_line = result

		elif v_etat:
			for vals in self:
				vals.env.cr.execute("""select m.dt_etat as dte, m.no_mandat as mdt, m.cd_rubrique_id as rub,
				m.no_beneficiaire as benef, m.obj as obj, m.mnt_ord as mnt from budg_mandat m
				where m.company_id = %s and m.x_exercice_id = %s and m.state = '%s' order by m.no_lo """ % (
				val_struct, val_ex, v_etat))

				rows = vals.env.cr.dictfetchall()
				result = []

				vals.mandat_line.unlink()
				for line in rows:
					result.append((0, 0, {'dte': line['dte'], 'no_mdt': line['mdt'], 'rubrique_id': line['rub'],
										  'beneficiaire_id': line['benef'], 'objet': line['obj'],
										  'montant': line['mnt']}))
				self.mandat_line = result


class BudgConsulMdtLine(models.Model):
	_name = "budg_consul_mandat_lines"

	mdt_id = fields.Many2one("budg_consul_mdt", ondelete='cascade')
	dte = fields.Date("Date")
	no_mdt = fields.Char("N° Mdt")
	objet = fields.Text("Objet")
	rubrique_id = fields.Many2one("budg_rubrique","Rubrique")
	montant = fields.Integer("Montant")
	beneficiaire_id = fields.Char("Bénéficiaire")


class BudgImprimer(models.Model):
	_name = "budg_imprimer"

	name = fields.Char(default="Etat d'exécution des dépenses")
	dte_debut = fields.Date("Du", required=True)
	dte_fin = fields.Date("Au", required=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice", readonly=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	imprimer_ids = fields.One2many("budg_imprimer_line","imprimer_id", readonly=True)

	def afficher(self):

		no_ex = int(self.x_exercice_id)
		cd_struct = int(self.company_id)

		self.env.cr.execute("DELETE FROM budg_imprimer_line")

		for vals in self:
			vals.env.cr.execute("select * from budg_ligne_exe_dep where company_id = %d and x_exercice_id = %d order by cd_titre_id, cd_section_id, cd_chapitre_id, cd_art_id, cd_paragraphe_id,cd_rubrique_id " % (cd_struct, no_ex))

			rows = vals.env.cr.dictfetchall()
			result = []

			vals.imprimer_ids.unlink()
			for line in rows:
				result.append((0, 0, {'titre': line['cd_titre_id'], 'section': line['cd_section_id'], 'chapitre': line['cd_chapitre_id'],
									  'article': line['cd_art_id'], 'paragraphe': line['cd_paragraphe_id'],'rubrique': line['cd_rubrique_id'],
									  'rubrique': line['cd_rubrique_id'],'initiale': line['mnt_budgetise'],'corrige': line['mnt_corrige']}))
			self.imprimer_ids = result

		self.CalculEngagement()
		self.CalculLiquidation()
		self.CalculMandat()

	def CalculEngagement(self):

		no_ex = int(self.x_exercice_id)
		cd_struct = int(self.company_id)
		deb = self.dte_debut
		fin = self.dte_fin

		self.env.cr.execute("""select sum(mnt_eng) as mnt,cd_titre_id, cd_section_id,
			 cd_chapitre_id, cd_article_id, cd_paragraphe_id, cd_rubrique_id from budg_engagement where dt_etat between %s and %s and company_id = %s and
			 x_exercice_id = %s and state not in ('draft','A') group by cd_titre_id, cd_section_id, cd_chapitre_id, cd_article_id, cd_paragraphe_id, cd_rubrique_id """ ,(deb, fin, cd_struct, no_ex))

		for val in self.env.cr.dictfetchall():
			eng = val['mnt']
			tit = val['cd_titre_id']
			sec = val['cd_section_id']
			chap = val['cd_chapitre_id']
			art = val['cd_article_id']
			par = val['cd_paragraphe_id']
			rub = val['cd_rubrique_id']

			self.env.cr.execute("""UPDATE budg_imprimer_line SET engagement = %s, taux = (%s/ corrige)*100 where titre = %s and section = %s and
			chapitre = %s and article = %s and paragraphe = %s and rubrique = %s and company_id = %s and 
			x_exercice_id = %s""" ,(eng, eng, tit, sec, chap, art, par, rub, cd_struct, no_ex))

	def CalculLiquidation(self):

		no_ex = int(self.x_exercice_id)
		cd_struct = int(self.company_id)
		deb = self.dte_debut
		fin = self.dte_fin

		self.env.cr.execute("""select sum(mnt_paye) as mnt,cd_titre_id, cd_section_id,
			 cd_chapitre_id, cd_article_id, cd_paragraphe_id, cd_rubrique_id from budg_liqord where dt_etat between %s and %s and company_id = %s and
			 x_exercice_id = %s and state not in ('draft','A','N') group by cd_titre_id, cd_section_id, cd_chapitre_id, cd_article_id, cd_paragraphe_id, cd_rubrique_id """ ,(deb, fin, cd_struct, no_ex))

		for val in self.env.cr.dictfetchall():
			liq = val['mnt']
			tit = val['cd_titre_id']
			sec = val['cd_section_id']
			chap = val['cd_chapitre_id']
			art = val['cd_article_id']
			par = val['cd_paragraphe_id']
			rub = val['cd_rubrique_id']

			self.env.cr.execute("""UPDATE budg_imprimer_line SET liquide = %s where titre = %s and section = %s and
			chapitre = %s and article = %s and paragraphe = %s and rubrique = %s and company_id = %s and 
			x_exercice_id = %s""" ,(liq, tit, sec, chap, art, par, rub, cd_struct, no_ex))


	def CalculMandat(self):

		no_ex = int(self.x_exercice_id)
		cd_struct = int(self.company_id)
		deb = self.dte_debut
		fin = self.dte_fin

		self.env.cr.execute("""select sum(mnt_ord) as mnt,cd_titre_id, cd_section_id,
			 cd_chapitre_id, cd_article_id, cd_paragraphe_id, cd_rubrique_id from budg_mandat where dt_etat between %s and %s and company_id = %s and
			 x_exercice_id = %s and state not in ('draft','A','N') group by cd_titre_id, cd_section_id, cd_chapitre_id, cd_article_id, cd_paragraphe_id, cd_rubrique_id """ ,(deb, fin, cd_struct, no_ex))

		for val in self.env.cr.dictfetchall():
			mdt = val['mnt']
			tit = val['cd_titre_id']
			sec = val['cd_section_id']
			chap = val['cd_chapitre_id']
			art = val['cd_article_id']
			par = val['cd_paragraphe_id']
			rub = val['cd_rubrique_id']

			self.env.cr.execute("""UPDATE budg_imprimer_line SET mandat = %s where titre = %s and section = %s and
			chapitre = %s and article = %s and paragraphe = %s and rubrique = %s and company_id = %s and 
			x_exercice_id = %s""" ,(mdt, tit, sec, chap, art, par, rub, cd_struct, no_ex))

	def get_report_values(self):

		company_id = int(self.company_id)
		x_exercice_id = int(self.x_exercice_id)

		doctitre = []
		self.env.cr.execute("SELECT cd_titre, coalesce(initi,0) as initi, lb_long, coalesce(corr,0) as corr, coalesce(eng,0) as eng, coalesce(liq,0) as liq, coalesce(mdt,0) as mdt, taux as taux FROM vue_sit_titre WHERE company_id = %d and x_exercice_id = %d" % (company_id, x_exercice_id))
		for line in self.env.cr.dictfetchall():

			v_titre = line['cd_titre']
			v_t_lib = line['lb_long']
			v_t_init = int(line['initi'])
			v_t_corr = line['corr']
			v_t_eng = line['eng']
			v_t_liq= line['liq']
			v_t_mdt = line['mdt']
			v_t_taux = round(line['taux'],2)

			# Boucle 2
			docsection = []
			self.env.cr.execute(
				"SELECT cd_titre, cd_section, coalesce(initi,0) as initi, lb_long, coalesce(corr,0) as corr, coalesce(eng,0) as eng, coalesce(liq,0) as liq, coalesce(mdt,0) as mdt, taux as taux FROM vue_sit_section WHERE company_id = %s and x_exercice_id = %s and cd_titre = '%s' " %(company_id, x_exercice_id,v_titre))
			for line in self.env.cr.dictfetchall():

				v_section = line['cd_section']
				v_s_lib = line['lb_long']
				v_s_init = int(line['initi'])
				v_s_corr = line['corr']
				v_s_eng = line['eng']
				v_s_liq = line['liq']
				v_s_mdt = line['mdt']
				v_s_taux = round(line['taux'],2)

				# Boucle 3
				docchapitre = []
				self.env.cr.execute(
					"SELECT cd_titre, cd_section, cd_chapitre, lb_long, coalesce(initi,0) as initi, coalesce(corr,0) as corr, coalesce(eng,0) as eng, coalesce(liq,0) as liq, coalesce(mdt,0) as mdt, taux as taux FROM vue_sit_chapitre WHERE company_id = %s and x_exercice_id = %s and cd_titre = '%s' and cd_section = '%s' " %(company_id, x_exercice_id, v_titre, v_section))

				for line in self.env.cr.dictfetchall():

					v_chapitre = line['cd_chapitre']
					v_c_lib = line['lb_long']
					v_c_init = int(line['initi'])
					v_c_corr = line['corr']
					v_c_eng = line['eng']
					v_c_liq = line['liq']
					v_c_mdt = line['mdt']
					v_c_taux = round(line['taux'],2)

					# Boucle 4
					docarticle = []
					self.env.cr.execute(
						"SELECT cd_titre, cd_section, cd_chapitre, cd_article, lb_long, coalesce(initi,0) as initi, coalesce(corr,0) as corr, coalesce(eng,0) as eng, coalesce(liq,0) as liq, coalesce(mdt,0) as mdt, taux as taux FROM vue_sit_article WHERE company_id = %s and x_exercice_id = %s and cd_titre = '%s' and cd_section = '%s' and cd_chapitre = '%s' " %(company_id, x_exercice_id, v_titre, v_section, v_chapitre))
					for line in self.env.cr.dictfetchall():

						v_article = line['cd_article']
						v_a_lib = line['lb_long']
						v_a_init = int(line['initi'])
						v_a_corr = line['corr']
						v_a_eng = line['eng']
						v_a_liq = line['liq']
						v_a_mdt = line['mdt']
						v_a_taux = round(line['taux'],2)

						# Boucle 4
						docparagraphe = []
						self.env.cr.execute(
							"SELECT cd_titre, cd_section, cd_chapitre, cd_article, cd_paragraphe, lb_long, coalesce(initi,0) as initi, coalesce(corr,0) as corr, coalesce(eng,0) as eng, coalesce(liq,0) as liq, coalesce(mdt,0) as mdt, taux as taux FROM vue_sit_paragraphe WHERE company_id = %s and x_exercice_id = %s and cd_titre = '%s' and cd_section = '%s' and cd_chapitre = '%s' and cd_article = '%s' " %(company_id, x_exercice_id, v_titre, v_section, v_chapitre, v_article))
						for line in self.env.cr.dictfetchall():

							v_paragraphe = line['cd_paragraphe']
							v_p_lib = line['lb_long']
							v_p_init = int(line['initi'])
							v_p_corr = line['corr']
							v_p_eng = line['eng']
							v_p_liq = line['liq']
							v_p_mdt = line['mdt']
							v_p_taux = round(line['taux'],2)

							docrubrique = []
							self.env.cr.execute(
								"SELECT cd_titre, cd_section, cd_chapitre, cd_article, cd_paragraphe, rubrique, lb_long, coalesce(initi,0) as initi, coalesce(corr,0) as corr, coalesce(eng,0) as eng, coalesce(liq,0) as liq, coalesce(mdt,0) as mdt, taux as taux FROM vue_sit_rubrique WHERE company_id = %s and x_exercice_id = %s and cd_titre = '%s' and cd_section = '%s' and cd_chapitre = '%s' and cd_article = '%s' and cd_paragraphe = '%s' " %(company_id, x_exercice_id, v_titre, v_section, v_chapitre, v_article,v_paragraphe))

							for line in self.env.cr.dictfetchall():
								v_rubrique = line['rubrique']
								v_r_lib = line['lb_long']
								v_r_init = int(line['initi'])
								v_r_corr = line['corr']
								v_r_eng = line['eng']
								v_r_liq = line['liq']
								v_r_mdt = line['mdt']
								v_r_taux = round(line['taux'],2)

								erubriq = {v_rubrique: [v_r_lib, v_r_init, v_r_corr, v_r_eng, v_r_liq, v_r_mdt, v_r_taux]}
								erubri = OrderedDict(sorted(erubriq.items(), key=lambda t: t[0]))
								docrubrique.append(erubri)

							eparagraphes = {v_paragraphe: [v_p_lib, v_p_init, v_p_corr, v_p_eng, v_p_liq, v_p_mdt, v_p_taux],'rubrique': docrubrique}
							eparagraphe = OrderedDict(sorted(eparagraphes.items(), key=lambda t: t[0]))
							docparagraphe.append(eparagraphe)

						earticles = {v_article: [v_a_lib, v_a_init, v_a_corr, v_a_eng, v_a_liq, v_a_mdt, v_a_taux],"paragraphe": docparagraphe}
						earticle = OrderedDict(sorted(earticles.items(), key=lambda t: t[0]))
						docarticle.append(earticle)

					echapitres = {v_chapitre: [v_c_lib, v_c_init, v_c_corr, v_c_eng, v_c_liq, v_c_mdt, v_c_taux], "article": docarticle}
					echapitre = OrderedDict(sorted(echapitres.items(), key=lambda t: t[0]))
					docchapitre.append(echapitre)

				esections = {v_section: [v_s_lib, v_s_init, v_s_corr, v_s_eng, v_s_liq, v_s_mdt, v_s_taux], "chapitre": docchapitre}
				esection = OrderedDict(sorted(esections.items(), key=lambda t: t[0]))
				docsection.append(esection)

			etitres = {v_titre: [v_t_lib, v_t_init, v_t_corr, v_t_eng, v_t_liq, v_t_mdt, v_t_taux], "section": docsection}
			etitre = OrderedDict(sorted(etitres.items(), key=lambda t: t[0]))
			doctitre.append(etitre)
			print("result", doctitre)

		return doctitre


class BudgImprimerLines(models.Model):
	_name = "budg_imprimer_line"

	imprimer_id = fields.Many2one("budg_imprimer", ondelete='cascade')
	titre = fields.Many2one("budg_titre", "Titre")
	section = fields.Many2one("budg_section", "Section")
	chapitre = fields.Many2one("budg_chapitre", "Chapitre")
	article = fields.Many2one("budg_param_article", "Article")
	paragraphe = fields.Many2one("budg_paragraphe", "Paragraphe")
	rubrique = fields.Many2one("budg_rubrique", "Rubrique")
	initiale = fields.Float("Dotation initiale")
	corrige = fields.Float("Dotation corrigée")
	engagement = fields.Float("Dépenses engagées")
	liquide = fields.Float("Dépenses liquidées")
	mandat = fields.Float("Mandats émis")
	taux = fields.Float("Taux d'exécution")
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice", readonly=True)
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)



class BudgViewTitre(models.Model):
	_name="vue_sit_titre"
	_auto=False

	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id,readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",
									default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),
									string="Exercice", readonly=True)
	cd_titre_id = fields.Many2one('budg_titre',string="Titre", readonly=True)
	somtitre = fields.Float('',readonly=True)

	@api.model
	def init(self):

		tools.drop_view_if_exists(self.env.cr, 'vue_sit_titre')

		self.env.cr.execute("""CREATE OR REPLACE VIEW vue_sit_titre AS (select l.company_id,l.x_exercice_id,rt.cd_titre, rt.lb_long,coalesce(SUM(l.initiale),0) as initi, coalesce(SUM(l.corrige),0) as corr, coalesce(SUM(l.engagement),0) as eng ,coalesce(SUM(l.liquide),0) as liq ,
		coalesce(SUM(l.mandat),0) as mdt, (coalesce(SUM(l.engagement),0)/ coalesce(SUM(l.corrige),0))*100 as taux FROM budg_imprimer_line l,budg_titre bt, ref_titre rt WHERE bt.id = l.titre and rt.id = bt.titre and l.corrige > 0 GROUP by l.company_id, l.x_exercice_id, l.titre, rt.cd_titre, rt.lb_long
		order by rt.cd_titre)""")




class BudgViewSection(models.Model):
	_name = "vue_sit_section"
	_auto = False

	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",
										default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),
										string="Exercice", readonly=True)
	cd_titre_id =fields.Many2one('budg_titre',string="Titre", readonly=True)
	cd_section_id = fields.Many2one('budg_section', string="Section", readonly=True)
	somsection = fields.Float('',readonly=True)



	@api.model
	def init(self):

		tools.drop_view_if_exists(self.env.cr, 'vue_sit_section')

		self.env.cr.execute("""CREATE OR REPLACE VIEW vue_sit_section AS (select l.company_id,l.x_exercice_id,rt.cd_titre,rs.cd_section, rs.lb_long,coalesce(SUM(l.initiale),0) as initi, coalesce(SUM(l.corrige),0) as corr, coalesce(SUM(l.engagement),0) as eng ,coalesce(SUM(l.liquide),0) as liq ,
		coalesce(SUM(l.mandat),0) as mdt, (coalesce(SUM(l.engagement),0)/ coalesce(SUM(l.corrige),0))*100 as taux FROM budg_imprimer_line l,budg_titre bt, ref_titre rt, budg_section bs, ref_section rs WHERE bt.id = l.titre and rt.id = bt.titre and bs.id = l.section and rs.id = bs.section and l.corrige > 0 
		GROUP by l.company_id, l.x_exercice_id, l.section, rt.cd_titre, rs.cd_section, rs.lb_long
		order by rt.cd_titre,rs.cd_section)""")


class BudgViewChapitre(models.Model):
	_name = "vue_sit_chapitre"
	_auto = False

	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",
									default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),
									string="Exercice", readonly=True)
	cd_titre_id =fields.Many2one('budg_titre',string="Titre", readonly=True)
	cd_section_id = fields.Many2one('budg_section', string="Section", readonly=True)
	cd_chapitre_id = fields.Many2one('budg_chapitre', string="Chapitre", readonly=True)
	somchapitre = fields.Float('',readonly=True)



	@api.model
	def init(self):

		tools.drop_view_if_exists(self.env.cr, 'vue_sit_chapitre')

		self.env.cr.execute("""CREATE OR REPLACE VIEW vue_sit_chapitre AS (select l.company_id,l.x_exercice_id,rt.cd_titre,rs.cd_section, rc.cd_chapitre, rc.lb_long,coalesce(SUM(l.initiale),0) as initi, coalesce(SUM(l.corrige),0) as corr, coalesce(SUM(l.engagement),0) as eng ,coalesce(SUM(l.liquide),0) as liq ,
		coalesce(SUM(l.mandat),0) as mdt, (coalesce(SUM(l.engagement),0)/ coalesce(SUM(l.corrige),0))*100 as taux FROM budg_imprimer_line l,budg_titre bt, ref_titre rt, budg_section bs, ref_section rs, budg_chapitre bc, ref_chapitre rc WHERE bt.id = l.titre and rt.id = bt.titre and bs.id = l.section and rs.id = bs.section and l.corrige > 0 
		and bc.id = l.chapitre and rc.id = bc.chapitre GROUP by l.company_id, l.x_exercice_id, l.section, rt.cd_titre, rs.cd_section, rc.cd_chapitre, rc.lb_long
		order by rt.cd_titre,rs.cd_section,rc.cd_chapitre)""")


class BudgViewArticle(models.Model):
	_name = "vue_sit_article"
	_auto = False

	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",
									default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),
									string="Exercice", readonly=True)
	cd_titre_id =fields.Many2one('budg_titre',string="Titre", readonly=True)
	cd_section_id = fields.Many2one('budg_section', string="Section", readonly=True)
	cd_chapitre_id = fields.Many2one('budg_chapitre', string="Chapitre", readonly=True)
	cd_article_id = fields.Many2one('budg_param_article', string="Article", readonly=True)
	somarticle = fields.Float('', readonly=True)


	@api.model
	def init(self):

		tools.drop_view_if_exists(self.env.cr, 'vue_sit_article')

		self.env.cr.execute("""CREATE OR REPLACE VIEW vue_sit_article AS (select l.company_id,l.x_exercice_id,rt.cd_titre,rs.cd_section, rc.cd_chapitre,ra.cd_article, ra.lb_long,coalesce(SUM(l.initiale),0) as initi, coalesce(SUM(l.corrige),0) as corr, coalesce(SUM(l.engagement),0) as eng ,coalesce(SUM(l.liquide),0) as liq ,
		coalesce(SUM(l.mandat),0) as mdt, (coalesce(SUM(l.engagement),0)/ coalesce(SUM(l.corrige),0))*100 as taux FROM budg_imprimer_line l,budg_titre bt, ref_titre rt, budg_section bs, ref_section rs, budg_chapitre bc, ref_chapitre rc,budg_param_article ba, ref_article ra
		WHERE bt.id = l.titre and rt.id = bt.titre and bs.id = l.section and rs.id = bs.section and l.corrige > 0 and bc.id = l.chapitre and rc.id = bc.chapitre and ba.id = l.article and ra.id = ba.article
		GROUP by l.company_id, l.x_exercice_id, l.section, rt.cd_titre, rs.cd_section, rc.cd_chapitre, ra.cd_article, ra.lb_long
		order by rt.cd_titre,rs.cd_section,rc.cd_chapitre,ra.cd_article)""")


class BudgVueSitPar(models.Model):
	_name = "vue_sit_paragraphe"
	_auto = False

	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",
									default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),
									string="Exercice", readonly=True)
	cd_titre_id =fields.Many2one('budg_titre',string="Titre", readonly=True)
	cd_section_id = fields.Many2one('budg_section', string="Section", readonly=True)
	cd_chapitre_id = fields.Many2one('budg_chapitre', string="Chapitre", readonly=True)
	cd_article_id = fields.Many2one('budg_param_article', string="Article", readonly=True)
	cd_paragraphe_id = fields.Many2one('budg_paragraphe', string="Paragraphe", readonly=True)
	sompara = fields.Float('',readonly=True)



	@api.model
	def init(self):
		tools.drop_view_if_exists(self.env.cr, 'vue_sit_paragraphe')

		self.env.cr.execute("""CREATE OR REPLACE VIEW vue_sit_paragraphe AS (select l.company_id,l.x_exercice_id,rt.cd_titre,rs.cd_section, rc.cd_chapitre,ra.cd_article,rp.cd_paragraphe, rp.lb_long,coalesce(SUM(l.initiale),0) as initi, coalesce(SUM(l.corrige),0) as corr, coalesce(SUM(l.engagement),0) as eng ,coalesce(SUM(l.liquide),0) as liq ,
		coalesce(SUM(l.mandat),0) as mdt, (coalesce(SUM(l.engagement),0)/ coalesce(SUM(l.corrige),0))*100 as taux FROM budg_imprimer_line l,budg_titre bt, ref_titre rt, budg_section bs, ref_section rs, budg_chapitre bc, ref_chapitre rc,budg_param_article ba, ref_article ra, budg_paragraphe bp, ref_paragraphe rp 
		WHERE bt.id = l.titre and rt.id = bt.titre and bs.id = l.section and rs.id = bs.section and l.corrige > 0 and bc.id = l.chapitre and rc.id = bc.chapitre and ba.id = l.article and ra.id = ba.article and bp.id = l.paragraphe and rp.id = bp.paragraphe
		GROUP by l.company_id, l.x_exercice_id, l.section, rt.cd_titre, rs.cd_section, rc.cd_chapitre, ra.cd_article, rp.cd_paragraphe, rp.lb_long
		order by rt.cd_titre,rs.cd_section,rc.cd_chapitre,ra.cd_article,rp.cd_paragraphe)""")


class BudgViewRubrique(models.Model):
	_name = "vue_sit_rubrique"
	_auto = False

	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id, readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",
									default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),
									string="Exercice", readonly=True)
	cd_titre_id =fields.Many2one('budg_titre',string="Titre", readonly=True)
	cd_section_id = fields.Many2one('budg_section', string="Section", readonly=True)
	cd_chapitre_id = fields.Many2one('budg_chapitre', string="Chapitre", readonly=True)
	cd_article_id = fields.Many2one('budg_param_article', string="Article", readonly=True)
	cd_paragraphe_id = fields.Many2one('budg_paragraphe', string="Paragraphe", readonly=True)
	cd_rubrique_id = fields.Many2one('budg_rubrique', string="Rubrique", readonly=True)
	somrub = fields.Float('',readonly=True)



	@api.model
	def init(self):
		tools.drop_view_if_exists(self.env.cr, 'vue_sit_rubrique')

		self.env.cr.execute("""CREATE OR REPLACE VIEW vue_sit_rubrique AS (select l.company_id,l.x_exercice_id,rt.cd_titre,rs.cd_section, rc.cd_chapitre,ra.cd_article,rp.cd_paragraphe,br.rubrique, br.lb_long,coalesce(SUM(l.initiale),0) as initi, coalesce(SUM(l.corrige),0) as corr, coalesce(SUM(l.engagement),0) as eng ,coalesce(SUM(l.liquide),0) as liq ,
		coalesce(SUM(l.mandat),0) as mdt, (coalesce(SUM(l.engagement),0)/ coalesce(SUM(l.corrige),0))*100 as taux FROM budg_imprimer_line l,budg_titre bt, ref_titre rt, budg_section bs, ref_section rs, budg_chapitre bc, ref_chapitre rc,budg_param_article ba, ref_article ra, budg_paragraphe bp, ref_paragraphe rp , budg_rubrique br 
		WHERE bt.id = l.titre and rt.id = bt.titre and bs.id = l.section and rs.id = bs.section and l.corrige > 0 and bc.id = l.chapitre and rc.id = bc.chapitre and ba.id = l.article and ra.id = ba.article and bp.id = l.paragraphe and rp.id = bp.paragraphe and br.id = l.rubrique
		GROUP by l.company_id, l.x_exercice_id, l.section, rt.cd_titre, rs.cd_section, rc.cd_chapitre, ra.cd_article, rp.cd_paragraphe,br.rubrique, br.lb_long
		order by rt.cd_titre,rs.cd_section,rc.cd_chapitre,ra.cd_article,rp.cd_paragraphe,br.rubrique)""")



class BudgFicheControle(models.Model):
	_name = "budg_fiche_controle"

	name = fields.Char(default="Fiche de contrôle des dépenses")
	cd_titre_id = fields.Many2one("budg_titre",default=lambda self: self.env['budg_titre'].search([('type_titre', '=', 'D')]),string="Titre", required=True)
	cd_section_id = fields.Many2one("budg_section", "Section", required=True)
	cd_chapitre_id = fields.Many2one("budg_chapitre", "Chapitre", required=True)
	cd_article_id = fields.Many2one("budg_param_article", "Article", required=True)
	cd_paragraphe_id = fields.Many2one("budg_paragraphe", "Paragraphe", required=True)
	cd_rubrique_id = fields.Many2one("budg_rubrique", "Rubrique", required=True)
	dt_appro_deb = fields.Date("Date debut", required=False)
	initiale = fields.Float("Dotation initiale", readonly=True)
	corrige = fields.Float("Dotation corrigé", readonly=True)
	engage = fields.Float("Crédits engagés", readonly=True)
	annule = fields.Float("Crédits annulés", readonly=True)
	disponibilite = fields.Float("Crédits disponible", readonly=True)
	taux = fields.Float("Taux d'excécution", digits = (20,2), readonly=True)
	x_exercice_id = fields.Many2one("ref_exercice",default=lambda self: self.env['ref_exercice'].search([('etat', '=', 1)]),string="Exercice")
	company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id.id)
	fiche_ids = fields.One2many("budg_fiche_controle_line","synthese_id", readonly=True)


	def afficher(self):
		
		v_ex = int(self.x_exercice_id)
		v_struct = int(self.company_id)
		val_rub = int(self.cd_rubrique_id)
		val_para = int(self.cd_paragraphe_id)
		val_art = int(self.cd_article_id)
		val_sec = int(self.cd_section_id)
		val_chap = int(self.cd_chapitre_id)
		val_titre = int(self.cd_titre_id)
		

		for vals in self:
			vals.env.cr.execute("""select * from budg_engagement where cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_article_id = %d and cd_paragraphe_id = %d
			and cd_rubrique_id = %d and company_id = %d and x_exercice_id = %d order by id""" % (val_titre, val_sec, val_chap, val_art, val_para, val_rub, v_struct,v_ex,))
			rows = vals.env.cr.dictfetchall()
			result = []

			vals.fiche_ids.unlink()
			for line in rows:
				result.append((0, 0, {'dte': line['dt_etat'], 'noeng': line['id'], 'objet': line['lb_obj'], 'montant': line['mnt_eng'],
									  'depense': line['cumul'],'dispo': line['credit_disponible'],'beneficiaire': line['no_beneficiaire'],
									  'etat': line['state']}))
			self.fiche_ids = result

		self.taux = (self.engage * 100) / self.corrige

	@api.onchange('cd_rubrique_id', 'cd_paragraphe_id', 'cd_article_id', 'cd_chapitre_id', 'cd_section_id','cd_titre_id')
	def cred_dipso(self):

		val_ex = int(self.x_exercice_id.id)
		val_struct = int(self.company_id.id)
		val_para = int(self.cd_paragraphe_id)
		val_rubrique = int(self.cd_rubrique_id)
		val_chap = int(self.cd_chapitre_id)
		val_sec = int(self.cd_section_id)
		val_tit = int(self.cd_titre_id)
		val_art = int(self.cd_article_id)

		result = self.env['budg_ligne_exe_dep'].search(
			[('cd_titre_id', '=', val_tit), ('cd_section_id', '=', val_sec), ('cd_chapitre_id', '=', val_chap),
			 ('cd_art_id', '=', val_art), ('cd_paragraphe_id', '=', val_para), ('cd_rubrique_id', '=', val_rubrique),
			 ('company_id', '=', val_struct), ('x_exercice_id', '=', val_ex)])

		self.disponibilite = result.mnt_disponible
		self.corrige = result.mnt_corrige
		self.engage = result.mnt_engage
		self.initiale = result.mnt_budgetise

		self.env.cr.execute("""select sum(mnt_eng) from budg_engagement where state = 'A' and cd_titre_id = %d and cd_section_id = %d and cd_chapitre_id = %d and cd_article_id = %d and cd_paragraphe_id = %d
		and cd_rubrique_id = %d and company_id = %d and x_exercice_id = %d""" % (val_tit, val_sec, val_chap, val_art, val_para, val_rubrique, val_struct,val_ex,))

		val = self.env.cr.fetchone()
		self.annule = val and val[0] or 0



class BudgFicheControleLine(models.Model):
	_name = 'budg_fiche_controle_line'

	synthese_id = fields.Many2one('budg_fiche_controle', ondelete='cascade')
	dte = fields.Date("Date", readonly=True)
	noeng = fields.Many2one("budg_engagement","N° eng", readonly=True)
	objet = fields.Text("Nature/objet de la dépense", readonly=True)
	beneficiaire = fields.Many2one("ref_beneficiaire", "Frns/Benef.")
	montant = fields.Integer("Montant", readonly=True)
	depense = fields.Float("Dépenses cumulées")
	dispo = fields.Float("Crédits disponibles")
	etat = fields.Selection([('draft','Brouillon'),('N','Confirmé'),('V','Approuvé'),('A','Annulé'),('R','Rejeté'),('LC','Liquidation en cours'),('L','Liquidé')],string="Etat")





