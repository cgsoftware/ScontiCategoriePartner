# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from osv.osv import except_osv
import time
from tools.translate import _
import decimal_precision as dp



class totfat_periodo(osv.osv_memory):
    _name = 'totfat_periodo'
    _description = 'Assegna le % di sconto per fatturato'
    _columns = {
                'dadata': fields.date('Da Data Documento', required=True ),
                'adata': fields.date('A Data Documento', required=True),
                }
    

    

    
    
    def calcola_sconti(self, cr, uid, ids, context=None):
        param = self.browse(cr, uid, ids)[0]
        oggi = time.strftime('%Y-%m-%d')
        partner_obj = self.pool.get('res.partner')
        cerca = [('fascia_sconto','!=',None)]
        ids_partner = partner_obj.search(cr,uid,cerca)
        if ids_partner:
            for partner in partner_obj.browse(cr,uid,ids_partner):
                cerca = [('partner_id','=',partner.id),('data_documento','>=',param.dadata),('data_documento','<=',param.adata)]
                ids_doc = self.pool.get('fiscaldoc.header').search(cr,uid,cerca)
                if ids_doc:
                    tot_merce = 0.0
                    for doc in self.pool.get('fiscaldoc.header').browse(cr,uid,ids_doc):
                        if doc.tipo_doc.tipo_documento<>"DT":
                            if doc.tipo_doc.tipo_documento=="NC":                            
                                tot_merce -= doc.totale_netto_merce
                            else:
                                tot_merce += doc.totale_netto_merce
                    if partner.fascia_sconto:
                        sc = partner.fascia_sconto.sconto_base_partner
                        for riga in partner.fascia_sconto.righe_fasce:
                            if tot_merce>= partner.fascia_sconto.da_importo and tot_merce<= partner.fascia_sconto.a_importo:
                                sc+= partner.fascia_sconto.sconto_fascia_partner
                    ok = partner_obj.write(cr,uid,partner.id,{'sconto_partner':sc,'data_elab_sconto':oggi})
            
        return {'type': 'ir.actions.act_window_close'}
        

totfat_periodo()
