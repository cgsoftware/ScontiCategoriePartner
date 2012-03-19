# -*- encoding: utf-8 -*-

import math

from osv import fields,osv
import tools
import ir
import pooler
from tools.translate import _
import decimal_precision as dp


class sconti_partner(osv.osv):
        _name = "sconti_partner"
        _description = "Fasce di Sconto Per Fatturato Partner"    
        _columns = {
                    'name':fields.char('Codice Sconto', size=5, required=True, translate=True),
                    'descriz':fields.char('Descrizione', size=25, translate=True),
                    'sconto_base_partner':fields.float('Sconto Base Partner', digits=(9, 3)),
                    'perc_provv':fields.float('Perc. Provvigione Agente', digits=(9, 3)),
                    'righe_fasce':fields.one2many('sconti_partner_righe', 'name', 'Fasce'),
                    'categ_escluse':fields.one2many('sconti_categ_escluse', 'name', 'Categorie Escluse'),
                    }
sconti_partner()

class sconti_partner_righe(osv.osv):
        _name = "sconti_partner_righe"
        _description = "Dettaglio Fasce di Sconto Per Fatturato Partner"    
        _columns = {
                    'name': fields.many2one('sconti_partner', 'Codice Fascia ', required=True, ondelete='cascade', select=True, readonly=True),
                    'da_importo':fields.float('Da Importo',digits_compute=dp.get_precision('Account')),
                    'a_importo':fields.float('A Importo',digits_compute=dp.get_precision('Account'), select=True),
                    'sconto_fascia_partner':fields.float('Sconto Fascia Partner', digits=(9, 3)),
                    }
sconti_partner_righe()


class sconti_categ_escluse(osv.osv):
        _name = "sconti_categ_escluse"
        _description = "Dettaglio Fasce di Sconto Per Fatturato Partner"    
        _columns = {
                    'name': fields.many2one('sconti_partner', 'Codice Fascia ', required=True, ondelete='cascade', select=True, readonly=True),
                    'categ_id': fields.many2one('product.category', 'Category', required=True),
                    }
sconti_categ_escluse()

class res_partner(osv.osv):
    _inherit='res.partner'
    _columns = {
		         'fascia_sconto':fields.many2one('sconti_partner', 'Fascia Sconto', select=False),
                 'data_elab_sconto': fields.date('Ultima Elaborazione', required=False, readonly=False),           
                }
    

res_partner()

class FiscalDocHeader(osv.osv):
   _inherit = "fiscaldoc.header"

   def onchange_partner_id(self, cr, uid, ids, part, context):
        #import pdb;pdb.set_trace()
        # cerca il cliente e poi riporta i dati che servono di default
        res = super(FiscalDocHeader,self).onchange_partner_id( cr, uid, ids, part, context)
        val = res.get('value',False)
        warning = res.get('warning',False)
        if val:
            
         if part:
            partner_obj = self.pool.get("res.partner")
            if partner_obj.browse(cr,uid,part).fascia_sconto:
                val['sconto_partner']= 0.0
                val['str_sconto_partner']=''
        return {'value': val, 'warning': warning}



FiscalDocHeader()

class FiscalDocRighe(osv.osv):
   _inherit = "fiscaldoc.righe"
   
   def onchange_articolo(self, cr, uid, ids, product_id, listino_id, qty, partner_id, data_doc, uom):
    res = super(FiscalDocRighe,self).onchange_articolo(cr, uid, ids, product_id, listino_id, qty, partner_id, data_doc, uom)
    v = res.get('value',False)
    #import pdb;pdb.set_trace()
    if v: 
     if partner_id:
        partner_obj = self.pool.get("res.partner")
        if partner_obj.browse(cr,uid,partner_id).fascia_sconto:
            # c'è lo sconto da tabella ed ora lo ribalta sulla riga dell'articolo
            v['discount_riga'] = partner_obj.browse(cr,uid,partner_id).sconto_partner
            v['prezzo_netto'] = self.calcola_netto(cr, uid, ids,v['product_prezzo_unitario'], v['discount_riga']) 
            v['totale_riga'] = self.totale_riga(cr,uid,qty, v['prezzo_netto'])   
            
            
    return {'value':v}    
       

FiscalDocRighe()



class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    
    
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):    
        res = super(sale_order_line,self).product_id_change( cr, uid, ids, pricelist, product, qty,uom, qty_uos, uos, name, partner_id,lang, update_tax, date_order, packaging, fiscal_position, flag)
        #import pdb;pdb.set_trace()  
        result = res.get('value',False)
        domain = res.get('domain',False)
        warning = res.get('warning',False)
        if partner_id:
         partner_obj = self.pool.get("res.partner")
         if partner_obj.browse(cr,uid,partner_id).fascia_sconto:
            # c'è lo sconto da tabella ed ora lo ribalta sulla riga dell'articolo
            result['discount'] = partner_obj.browse(cr,uid,partner_id).sconto_partner
        
        
        return {'value': result, 'domain': domain, 'warning': warning}

sale_order_line()