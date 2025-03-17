from flask import Flask, render_template, request, redirect
from flask import url_for
from flask_bootstrap import Bootstrap
import pandas as pd
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.models import (HoverTool, ResetTool)
from bokeh.embed import file_html
from bokeh.layouts import layout
from bokeh.models import ColumnDataSource,Legend
from bokeh.models import Div,SaveTool
from bokeh.models import ColumnDataSource, RangeSlider, BoxAnnotation, CustomJS
import os
import sqlalchemy
from sqlalchemy import text
from bokeh.models.widgets import Select
from bokeh.models import DataRange1d
from bokeh.transform import factor_cmap
from bokeh.plotting import figure, output_file, save

#初期設定
app = Flask(__name__)
bootstrap=Bootstrap(app)
df_tf = pd.read_csv("./example/df_qtl_example.csv", delimiter=",",index_col=None)
df_ukb_base = pd.read_csv("./example/df_ukb_example.csv", delimiter=",",index_col=None)
df_ems_base = pd.read_csv("./example/df_ems_example.csv", delimiter=",",index_col=None)
df_mpra_base = pd.read_csv("./example/df_mpra_gene.csv", delimiter=",",index_col=None)


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        input_value = request.form['input_value'] 
        if input_value.startswith('chr') or input_value.startswith('rs'):
            return redirect(url_for('variant',input_value=input_value))
        else:
            return redirect(url_for('gene',input_value=input_value))
    return render_template("index.html")
    
@app.route('/variant')
def variant():
    input_value = request.args.get('input_value')
    if input_value.startswith('chr'):
        df_qtl = df_tf[df_tf["variant_id_hg38"]==input_value]  
        if len(df_qtl) == 0:
            error_message = f"No data found for input value: {input_value}"
            return render_template('index.html', error_message=error_message)
        else:
            variant = input_value.split("chr")[1].split(":")
            return render_template('variant.html', df_qtl=df_qtl,title_name=input_value,var=variant)  
        
    elif input_value.startswith('rs'):
        df_qtl = df_tf[df_tf["rsid"]==input_value]  
        if len(df_qtl) == 0:
            error_message = f"No data found for input value: {input_value}"
            return render_template('index.html', error_message=error_message)
        else:
            variant = df_qtl['variant_id_hg38'].values[0].split("chr")[1].split(":")
            return render_template('variant.html', df_qtl=df_qtl,title_name=input_value,var=variant)  
    else:
        error_message = f"No data found for input value: {input_value}"
        return render_template('index.html', error_message=error_message)

@app.route('/gene', methods=['GET'])
def gene():
    input_value = request.args.get('input_value')
    input_value = input_value.upper()
    if input_value.startswith('ENSG'):
        input_value = input_value.split('.')[0]
        df_qtl = df_tf[df_tf["gene_id"]==input_value]    
        df_ems = df_ems_base[df_ems_base["gene_id"]==input_value]
        df_mpra = df_mpra_base[df_mpra_base["gene_id"]==input_value]
        df_ukb = df_ukb_base[df_ukb_base["gene_id"]==input_value]

        if len(df_qtl) == 0:
            error_message = f"No data found for input value: {input_value}"
            return render_template('index.html', error_message=error_message)
        else:
            gene_name = df_qtl['gene_name'].values[0]
            gene_id = input_value      
    else:
        df_qtl = df_tf[df_tf["gene_name"]==input_value]   
        df_ems = df_ems_base[df_ems_base["gene_name"]==input_value]
        df_mpra = df_mpra_base[df_mpra_base["gene_name"]==input_value]
        df_ukb = df_ukb_base[df_ukb_base["gene_name"]==input_value]

        if len(df_qtl) == 0:
            error_message = f"No data found for input value: {input_value}"
            return render_template('index.html', error_message=error_message)
        else:
            gene_name = input_value
            gene_id = df_qtl['gene_id'].values[0]

    df_k562 = df_mpra[df_mpra["cell_type"]=="K562"] 
    df_hepg2 = df_mpra[df_mpra["cell_type"]=="HepG2"] 

    #1 QTL plots: データソースを作成
    source_eqtl = ColumnDataSource(data=df_qtl[df_qtl['category']=="eQTL"])
    source_pqtl = ColumnDataSource(data=df_qtl[df_qtl['category']=="pQTL"])

    source_eqtl.data['y']=source_eqtl.data['pip_susie'] #default y
    source_pqtl.data['y']=source_pqtl.data['pip_susie'] #default y

    #2 UKBB plots: データソースを作成
    source_cardiovascular = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Cardiovascular"])
    source_hematopoietic = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Hematopoietic"])
    source_hepatic = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Hepatic"])
    source_immunological = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Immunological"])
    source_lipids = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Lipids"])
    source_metabolic = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Metabolic"])
    source_neurological = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Neurological"])
    source_other = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Other"])
    source_psychological = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Psychological"])
    source_renal = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Renal"])
    source_skeletal = ColumnDataSource(data=df_ukb[df_ukb['categ']=="Skeletal"])

    source_cardiovascular.data['y']=source_cardiovascular.data['pip'] #default y
    source_hematopoietic.data['y']=source_hematopoietic.data['pip'] #default y
    source_hepatic.data['y']=source_hepatic.data['pip'] #default y
    source_immunological.data['y']=source_immunological.data['pip'] #default y
    source_lipids.data['y']=source_lipids.data['pip'] #default y
    source_metabolic.data['y']=source_metabolic.data['pip'] #default y
    source_neurological.data['y']=source_neurological.data['pip'] #default y
    source_other.data['y']=source_other.data['pip'] #default y
    source_psychological.data['y']=source_psychological.data['pip'] #default y
    source_renal.data['y']=source_renal.data['pip'] #default y
    source_skeletal.data['y']=source_skeletal.data['pip'] #default y

    #3 EMS plots: データソースを作成
    source_ems = ColumnDataSource(df_ems) # ColumnDataSourceにデータを格納
    source_ems.data['y5']=source_ems.data['Whole_Blood'] #default y

    # HoverToolの設定
    hover_qtl = HoverTool(tooltips=[("Variant ID", "@variant_id_hg38"),
                                ("Category", "@category"),
                                ("P-value", "@pval_nominal"),
                                ("PIP(SuSiE)", "@pip_susie"),
                                ("Effect Size", "@slope")]) 
    hover_ukb = HoverTool(tooltips=[("Variant ID", "@variant_id_hg38"),
                                ("Category", "@categ"),
                                ("Trait", "@trait"),
                                ("PIP(SuSiE)", "@pip"),])
    hover_ems = HoverTool(tooltips=[("Variant ID", "@variant_id_hg38")])
    hover_mpra = HoverTool(tooltips=[("Variant ID", "@variant_id_hg38"),
                                     ("P-Value", "@pval"),
                                     ("logFC", "@alpha_diff")]) 

    #1 QTL plots
    plot_qtl = figure(width=1080, height=220, title="PIP",title_location="left",x_axis_label=f'Distance to TSS of {gene_name}', tools=[hover_qtl,SaveTool()],x_range=([-1e6, 1e6]),y_range = [0, 1.06])
    plot_qtl.title.text_font_size = "14pt"
    plot_qtl.title.align = "center"
    plot_qtl.title.text_font_style = "normal"
    plot_qtl.xgrid.grid_line_alpha = 0.5
    plot_qtl.ygrid.grid_line_color = None
    glyph_eqtl = plot_qtl.circle('tss_distance', 'y',fill_alpha=0.5, size=14, color='royalblue', source=source_eqtl)
    glyph_pqtl = plot_qtl.circle('tss_distance', 'y',fill_alpha=0.5, size=14, color='orange', source=source_pqtl)

    legend = Legend(items=[( "eQTL", [glyph_eqtl]), ("pQTL", [glyph_pqtl])], location='top_right')
    plot_qtl.add_layout(legend)
    legend.click_policy = "hide"
    options_qtl = ['P-value','PIP (SuSiE)','PIP (FINEMAP)'] 
    select_qtl = Select(options=options_qtl,value='PIP (SuSiE)') 

    callback_qtl = CustomJS(args=dict(source_eqtl=source_eqtl, source_pqtl=source_pqtl, select=select_qtl, title=plot_qtl.title, y_range=plot_qtl.y_range), code="""
        var selected_category = select.value;
        if (selected_category == "P-value") {
            source_eqtl.data['y'] = source_eqtl.data['pval_log'];
            source_pqtl.data['y'] = source_pqtl.data['pval_log'];
            title.text = "-log10(p-value)";
            
            // y_rangeの最大値を繰り上げる処理
            let maxValue = Math.max(...source_eqtl.data['y'], ...source_pqtl.data['y']);
            let roundedUpMaxValue = Math.ceil(maxValue / 10) * 10;  
            
            // y軸設定
            y_range.start = 0;
            y_range.end = roundedUpMaxValue;
        } else if (selected_category == "PIP (SuSiE)") {
            source_eqtl.data['y'] = source_eqtl.data['pip_susie'];
            source_pqtl.data['y'] = source_pqtl.data['pip_susie'];
            title.text = "PIP";
            
            // y軸設定
            y_range.start = 0;
            y_range.end = 1.06;
        } else if (selected_category == "PIP (FINEMAP)") {
            source_eqtl.data['y'] = source_eqtl.data['pip_fm'];
            source_pqtl.data['y'] = source_pqtl.data['pip_fm'];
            title.text = "PIP";
            
            // y軸設定
            y_range.start = 0;
            y_range.end = 1.06;
        }
        source_eqtl.change.emit();
        source_pqtl.change.emit();
    """)

    select_qtl.js_on_change('value', callback_qtl)

    slider_qtl = RangeSlider(title=" Adjust X-Axis range",start=-1e6,end=1e6,step=10,value=(-1e6, 1e6),width_policy="max")
    slider_qtl.js_link("value", plot_qtl.x_range, "start", attr_selector=0)
    slider_qtl.js_link("value", plot_qtl.x_range, "end", attr_selector=1) 
    slider_qtl.margin = (0, 0, 0, 30)
    slider_qtl.bar_color = "cornflowerblue"
    
    #2 UKBB plots
    plot_ukb = figure(width=1080, height=260, title="UKB PIP",title_location="left",x_axis_label=f'Distance to TSS of {gene_name}', tools=[hover_ukb,ResetTool(),SaveTool()],x_range=([-1e6, 1e6]),y_range = [0, 1.06])
    plot_ukb.title.text_font_size = "14pt"
    plot_ukb.title.align = "center"
    plot_ukb.title.text_font_style = "normal"
    plot_ukb.xgrid.grid_line_alpha = 0.5
    plot_ukb.ygrid.grid_line_color = None

    glyph_cardiovascular = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='skyblue', source=source_cardiovascular)
    glyph_hematopoietic = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='salmon', source=source_hematopoietic)
    glyph_hepatic = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='olive', source=source_hepatic)
    glyph_immunological = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='indianred', source=source_immunological)
    glyph_lipids = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='darkorchid', source=source_lipids)
    glyph_metabolic = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='saddlebrown', source=source_metabolic)
    glyph_neurological = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='lightpink', source=source_neurological)
    glyph_other = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='dimgray', source=source_other)
    glyph_psychological = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='limegreen', source=source_psychological)
    glyph_renal = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='steelblue', source=source_renal)
    glyph_skeletal = plot_ukb.circle('tss_distance', 'y', fill_alpha=0.5, size=14, color='khaki', source=source_skeletal)
 
    legend_ukb = Legend(items=[( "Cardiovascular   ", [glyph_cardiovascular]), ("Hematopoietic   ", [glyph_hematopoietic]), ("Hepatic   ", [glyph_hepatic]), ("Immunological   ", [glyph_immunological]), ("Lipids   ", [glyph_lipids]), ("Metabolic   ", [glyph_metabolic]), ("Neurological   ", [glyph_neurological]), ("Other   ", [glyph_other]), ("Psychological   ", [glyph_psychological]), ("Renal   ", [glyph_renal]), ("Skeletal   ", [glyph_skeletal])],
                    location='top_center', orientation='horizontal')
    plot_ukb.add_layout(legend_ukb, 'above')
    legend_ukb.click_policy = "hide"
    slider_ukb = RangeSlider(title=" Adjust X-Axis range",start=-1e6,end=1e6,step=10,value=(-1e6, 1e6),width_policy="max")
    slider_ukb.js_link("value", plot_ukb.x_range, "start", attr_selector=0) 
    slider_ukb.js_link("value", plot_ukb.x_range, "end", attr_selector=1) 
    slider_ukb.margin = (0, 0, 0, 30) 
    slider_ukb.bar_color = "cornflowerblue" 

    #3 EMS plots
    plot_ems = figure(width=1080, height=220, y_axis_label="EMS",x_axis_label=f'Distance to TSS of {gene_name}',tools=[hover_ems, ResetTool(),SaveTool()], x_range=([-1e6, 1e6]))
    plot_ems.circle('tss_distance', 'y5',color='green',fill_alpha=0.5, size=14, source=source_ems)
    plot_ems.y_range = DataRange1d(start=0, follow="end")
    plot_ems.yaxis.axis_label_text_font_size = "14pt"
    plot_ems.yaxis.axis_label_text_font_style = "normal"
    plot_ems.xgrid.grid_line_alpha = 0.5
    plot_ems.ygrid.grid_line_color = None

    options_ems= ['Whole_Blood', 'Muscle_Skeletal', 'Liver', 'Brain_Cerebellum','Prostate', 'Spleen', 'Skin_Sun_Exposed_Lower_leg', 'Artery_Coronary',
                                   'Esophagus_Muscularis', 'Esophagus_Gastroesophageal_Junction','Artery_Tibial', 'Heart_Atrial_Appendage', 'Nerve_Tibial',
                                   'Heart_Left_Ventricle', 'Adrenal_Gland', 'Adipose_Visceral_Omentum','Pancreas', 'Lung', 'Pituitary',
                                   'Brain_Nucleus_accumbens_basal_ganglia', 'Colon_Transverse','Adipose_Subcutaneous', 'Esophagus_Mucosa', 'Brain_Cortex', 'Thyroid',
                                   'Stomach', 'Breast_Mammary_Tissue', 'Colon_Sigmoid','Skin_Not_Sun_Exposed_Suprapubic', 'Testis', 'Artery_Aorta',
                                   'Brain_Amygdala', 'Brain_Anterior_cingulate_cortex_BA24','Brain_Caudate_basal_ganglia', 'Brain_Cerebellar_Hemisphere',
                                   'Brain_Frontal_Cortex_BA9', 'Brain_Hippocampus', 'Brain_Hypothalamus','Brain_Putamen_basal_ganglia', 'Brain_Spinal_cord_cervical_c-1',
                                   'Brain_Substantia_nigra', 'Cells_Cultured_fibroblasts','Cells_EBV-transformed_lymphocytes', 'Kidney_Cortex',
                                   'Minor_Salivary_Gland', 'Ovary', 'Small_Intestine_Terminal_Ileum','Uterus', 'Vagina']
    select_ems = Select(options=options_ems,value='Whole_Blood') 
    callback_ems = CustomJS(args=dict(source_ems=source_ems, y_axis3=select_ems), code="""
        const data = source_ems.data; // ColumnDataSourceのデータを取得
        const y5 = y_axis3.value; // セレクトボックスの値を取得
        data['y5'] = data[y5]; // y軸の値を更新
        source_ems.change.emit(); // ColumnDataSourceを更新
    """)
    select_ems.js_on_change('value',callback_ems)
    slider_ems = RangeSlider(title=" Adjust X-Axis range",start=-1e6,end=1e6,step=10,value=(-1e6, 1e6),width_policy="max")
    slider_ems.js_link("value", plot_ems.x_range, "start", attr_selector=0) 
    slider_ems.js_link("value", plot_ems.x_range, "end", attr_selector=1) 
    slider_ems.margin = (0, 0, 0, 30) 
    slider_ems.bar_color = "cornflowerblue" 

    #4 MPRA plots
    def create_plot(df, df_k562, df_hepg2, value):
        source_mpra = ColumnDataSource(df) 
        colors = factor_cmap('Tier', palette=['#BEE026', '#21918D', '#7F7F7F'], factors=['Tier 1', 'Tier 2', 'None'])
        
        plot_mpra = figure(width=1080, height=220,y_axis_label="Log2(Alt/Ref)",x_axis_label=f'Distance to TSS of {gene_name}',tools=[hover_mpra, ResetTool(),SaveTool()],x_range=([-1e6, 1e6]),y_range = [-3, 3])
        plot_mpra.circle('tss_distance', 'alpha_diff', fill_alpha=0.5, size=14, source=source_mpra, color=colors, legend_field='Tier')
        plot_mpra.yaxis.axis_label_text_font_size = "14pt" 
        plot_mpra.yaxis.axis_label_text_font_style = "normal" 
        plot_mpra.xgrid.grid_line_alpha = 0.5
        plot_mpra.ygrid.ticker = [-3, 0, 3] 
        
        select_mpra = Select(options=['Expression Fold Change(K562)', 'Expression Fold Change(HepG2)'], value=value)
        
        callback_code = """
            var selected_value = cb_obj.value;
            var data = source_mpra.data;

            if (selected_value == 'Expression Fold Change(K562)') {
                data['tss_distance'] = %s;
                data['alpha_diff'] = %s;
                data['Tier'] = %s;
                data['variant_id_hg38'] = %s;
                data['pval'] = %s;
            } else if (selected_value == 'Expression Fold Change(HepG2)') {
                data['tss_distance'] = %s;
                data['alpha_diff'] = %s;
                data['Tier'] = %s;
                data['variant_id_hg38'] = %s;
                data['pval'] = %s;
            }

            source_mpra.change.emit();
        """
        select_mpra.js_on_change('value', CustomJS(args=dict(source_mpra=source_mpra), code=callback_code % (
            df_k562['tss_distance'].to_list(), df_k562['alpha_diff'].to_list(), df_k562['Tier'].to_list(), df_k562['variant_id_hg38'].to_list(), df_k562['pval'].to_list(),
            df_hepg2['tss_distance'].to_list(), df_hepg2['alpha_diff'].to_list(), df_hepg2['Tier'].to_list(), df_hepg2['variant_id_hg38'].to_list(), df_hepg2['pval'].to_list()
        )))
        return select_mpra, plot_mpra

    if len(df_k562) >= len(df_hepg2):
        select_mpra, plot_mpra = create_plot(df_k562, df_k562, df_hepg2,'Expression Fold Change(K562)')
    else:
        select_mpra, plot_mpra = create_plot(df_hepg2, df_k562, df_hepg2,'Expression Fold Change(HepG2)')

    slider_mpra = RangeSlider(title=" Adjust X-Axis range",start=-1e6,end=1e6,step=10,value=(-1e6, 1e6),width_policy="max")
    slider_mpra.js_link("value", plot_mpra.x_range, "start", attr_selector=0) 
    slider_mpra.js_link("value", plot_mpra.x_range, "end", attr_selector=1) 
    slider_mpra.margin = (0, 0, 0, 30) 
    slider_mpra.bar_color = "cornflowerblue" 

    div1 = Div(width=200,height=30) 
    div2 = Div(width=200,height=30)
    div3 = Div(width=200,height=30)
    div4 = Div(width=200,height=30) 
    div5 = Div(width=200,height=30)
    div6 = Div(width=200,height=30)   
    div7 = Div(width=200,height=30) 
    div8 = Div(width=200,height=30)
    div9 = Div(width=200,height=30)
    
    # create layout and add plots
    layout_qtl = layout([div1,div2,div3,select_qtl],[plot_qtl],[slider_qtl], sizing_mode='stretch_width')
    layout_ukb = layout([plot_ukb],[slider_ukb], sizing_mode='stretch_width')
    layout_ems = layout([div4,div5,div6,select_ems],[plot_ems],[slider_ems], sizing_mode='stretch_width')
    layout_mpra = layout([div7,div8,div9,select_mpra],[plot_mpra],[slider_mpra], sizing_mode='stretch_width')

    html_qtl = file_html(layout_qtl, CDN, "qtl plot") 
    html_ukb = file_html(layout_ukb, CDN, "ukb plot") 
    html_ems = file_html(layout_ems, CDN, "ems plot") 
    html_mpra = file_html(layout_mpra, CDN, "mpra plot") 
    return render_template('gene.html', html_qtl=html_qtl,html_ukb=html_ukb,html_ems=html_ems,html_mpra=html_mpra,df_qtl=df_qtl,gene_name=gene_name,gene_id=gene_id,df_ems=df_ems,df_mpra=df_mpra, df_ukb=df_ukb)

@app.route('/download')
def download_page():
    return render_template('download.html')

@app.route('/about')
def about_page():
    return render_template('about.html')
s

if __name__ == "__main__":
    app.run(debug=True)

