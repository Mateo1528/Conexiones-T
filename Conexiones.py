import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import pi, sqrt, sin, cos, radians

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Conexiones de Acero",
    page_icon="🔧",
    layout="wide"
)

st.title("🔧 Calculadora de Conexiones Atornilladas y Soldadas")
st.markdown("---")

# Sidebar para selección del tipo de conexión
st.sidebar.header("Tipo de Conexión")
connection_type = st.sidebar.selectbox(
    "Selecciona el tipo de conexión:",
    ["Conexión Atornillada", "Conexión Soldada"]
)

# Propiedades del acero comunes
steel_grades = {
    "A36": {"Fy": 250, "Fu": 400},
    "A572 Gr50": {"Fy": 345, "Fu": 450},
    "A992": {"Fy": 345, "Fu": 450}
}

if connection_type == "Conexión Atornillada":
    st.header("📌 Diseño de Conexión Atornillada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros del Material")
        steel_grade = st.selectbox("Grado del acero:", list(steel_grades.keys()))
        Fy = steel_grades[steel_grade]["Fy"]  # MPa
        Fu = steel_grades[steel_grade]["Fu"]  # MPa
        
        st.subheader("Geometría de la Placa")
        plate_thickness = st.number_input("Espesor de placa (mm):", min_value=5.0, value=12.0, step=1.0)
        plate_width = st.number_input("Ancho de placa (mm):", min_value=50.0, value=200.0, step=10.0)
        
        st.subheader("Especificaciones del Perno")
        bolt_diameter = st.selectbox("Diámetro del perno (mm):", [12, 16, 20, 24, 27, 30])
        bolt_grade = st.selectbox("Grado del perno:", ["A325", "A490"])
        num_bolts = st.number_input("Número de pernos:", min_value=1, value=4, step=1)
        
        # Propiedades del perno
        bolt_properties = {
            "A325": {"Fnt": 620, "Fnv": 372},  # MPa
            "A490": {"Fnt": 780, "Fnv": 468}   # MPa
        }
        
    with col2:
        st.subheader("Cargas Aplicadas")
        P_tension = st.number_input("Carga de tensión (kN):", min_value=0.0, value=100.0, step=10.0)
        P_shear = st.number_input("Carga de corte (kN):", min_value=0.0, value=50.0, step=10.0)
        
        st.subheader("Configuración Geométrica")
        edge_distance = st.number_input("Distancia al borde (mm):", min_value=20.0, value=40.0, step=5.0)
        bolt_spacing = st.number_input("Espaciamiento entre pernos (mm):", min_value=50.0, value=80.0, step=10.0)
        
    # Cálculos
    if st.button("Calcular Capacidad de Conexión Atornillada"):
        # Área del perno
        Ab = pi * (bolt_diameter/2)**2  # mm²
        
        # Capacidades del perno
        Fnt = bolt_properties[bolt_grade]["Fnt"]
        Fnv = bolt_properties[bolt_grade]["Fnv"]
        
        # Capacidad a tensión del perno
        Pnt = 0.75 * Fnt * Ab / 1000  # kN (factor de resistencia φ = 0.75)
        
        # Capacidad a corte del perno
        Pnv = 0.75 * Fnv * Ab / 1000  # kN
        
        # Capacidad total de la conexión
        total_tension_capacity = num_bolts * Pnt
        total_shear_capacity = num_bolts * Pnv
        
        # Verificación de la placa (desgarramiento por corte)
        hole_diameter = bolt_diameter + 2  # mm (holgura estándar)
        net_area = plate_thickness * (plate_width - num_bolts * hole_diameter)  # mm²
        
        # Capacidad de la placa a tensión
        plate_tension_capacity = 0.75 * Fu * net_area / 1000  # kN
        
        # Capacidad de la placa a corte
        gross_area = plate_thickness * plate_width  # mm²
        plate_shear_capacity = 0.6 * 0.9 * Fy * gross_area / 1000  # kN
        
        # Resultados
        st.subheader("📊 Resultados del Análisis")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**Capacidades de los Pernos:**")
            st.write(f"• Capacidad a tensión por perno: {Pnt:.1f} kN")
            st.write(f"• Capacidad a corte por perno: {Pnv:.1f} kN")
            st.write(f"• Capacidad total a tensión: {total_tension_capacity:.1f} kN")
            st.write(f"• Capacidad total a corte: {total_shear_capacity:.1f} kN")
            
        with col4:
            st.write("**Capacidades de la Placa:**")
            st.write(f"• Capacidad a tensión: {plate_tension_capacity:.1f} kN")
            st.write(f"• Capacidad a corte: {plate_shear_capacity:.1f} kN")
            st.write(f"• Área neta: {net_area:.0f} mm²")
            
        # Verificaciones
        st.subheader("✅ Verificaciones de Diseño")
        
        # Factor de utilización
        tension_utilization = P_tension / min(total_tension_capacity, plate_tension_capacity)
        shear_utilization = P_shear / min(total_shear_capacity, plate_shear_capacity)
        
        combined_utilization = sqrt(tension_utilization**2 + shear_utilization**2)
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            if tension_utilization <= 1.0:
                st.success(f"✅ Tensión OK: {tension_utilization:.2f}")
            else:
                st.error(f"❌ Tensión FALLA: {tension_utilization:.2f}")
                
        with col6:
            if shear_utilization <= 1.0:
                st.success(f"✅ Corte OK: {shear_utilization:.2f}")
            else:
                st.error(f"❌ Corte FALLA: {shear_utilization:.2f}")
                
        with col7:
            if combined_utilization <= 1.0:
                st.success(f"✅ Combinada OK: {combined_utilization:.2f}")
            else:
                st.error(f"❌ Combinada FALLA: {combined_utilization:.2f}")
        
        # Gráfico de la conexión atornillada
        if st.checkbox("Mostrar Gráfico de la Conexión"):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Gráfico 1: Esquema de la conexión
            ax1.set_xlim(0, plate_width + 20)
            ax1.set_ylim(0, 150)
            
            # Dibujar placa
            plate = plt.Rectangle((10, 50), plate_width, plate_thickness*3, 
                                fill=False, edgecolor='black', linewidth=2)
            ax1.add_patch(plate)
            
            # Dibujar pernos
            bolt_positions = []
            for i in range(num_bolts):
                x_pos = 10 + edge_distance + i * bolt_spacing
                if x_pos <= plate_width - edge_distance:
                    bolt = plt.Circle((x_pos, 50 + plate_thickness*1.5), 
                                    bolt_diameter/4, color='red', alpha=0.7)
                    ax1.add_patch(bolt)
                    bolt_positions.append(x_pos)
            
            ax1.set_title("Esquema de la Conexión Atornillada")
            ax1.set_xlabel("Distancia (mm)")
            ax1.set_ylabel("Altura (mm)")
            ax1.grid(True, alpha=0.3)
            ax1.set_aspect('equal')
            
            # Gráfico 2: Comparación de capacidades vs cargas
            categories = ['Tensión', 'Corte']
            loads = [P_tension, P_shear]
            capacities = [min(total_tension_capacity, plate_tension_capacity),
                         min(total_shear_capacity, plate_shear_capacity)]
            
            x = np.arange(len(categories))
            width = 0.35
            
            ax2.bar(x - width/2, loads, width, label='Cargas Aplicadas', color='red', alpha=0.7)
            ax2.bar(x + width/2, capacities, width, label='Capacidades', color='green', alpha=0.7)
            
            ax2.set_xlabel('Tipo de Carga')
            ax2.set_ylabel('Fuerza (kN)')
            ax2.set_title('Cargas vs Capacidades')
            ax2.set_xticks(x)
            ax2.set_xticklabels(categories)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            st.pyplot(fig)

else:  # Conexión Soldada
    st.header("🔥 Diseño de Conexión Soldada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Parámetros del Material")
        steel_grade = st.selectbox("Grado del acero:", list(steel_grades.keys()))
        Fy = steel_grades[steel_grade]["Fy"]  # MPa
        
        st.subheader("Especificaciones de la Soldadura")
        weld_type = st.selectbox("Tipo de soldadura:", ["Filete", "Penetración Completa"])
        electrode = st.selectbox("Electrodo:", ["E70XX (485 MPa)", "E80XX (550 MPa)"])
        
        # Resistencia del electrodo
        electrode_strength = {"E70XX (485 MPa)": 485, "E80XX (550 MPa)": 550}
        FEXX = electrode_strength[electrode]
        
        weld_size = st.number_input("Tamaño de soldadura (mm):", min_value=3.0, value=6.0, step=1.0)
        weld_length = st.number_input("Longitud de soldadura (mm):", min_value=50.0, value=200.0, step=10.0)
        
    with col2:
        st.subheader("Geometría de Elementos")
        plate_thickness = st.number_input("Espesor de placa (mm):", min_value=5.0, value=12.0, step=1.0)
        connection_angle = st.slider("Ángulo de la carga respecto a la soldadura (°):", 0, 90, 0)
        
        st.subheader("Cargas Aplicadas")
        P_applied = st.number_input("Carga aplicada (kN):", min_value=0.0, value=100.0, step=10.0)
        M_applied = st.number_input("Momento aplicado (kN·m):", min_value=0.0, value=0.0, step=5.0)
        
    # Cálculos para soldadura
    if st.button("Calcular Capacidad de Conexión Soldada"):
        if weld_type == "Filete":
            # Soldadura de filete
            # Área efectiva de la soldadura
            throat_thickness = 0.707 * weld_size  # mm
            effective_area = throat_thickness * weld_length  # mm²
            
            # Resistencia de la soldadura de filete
            Fnw = 0.60 * FEXX  # MPa
            weld_capacity = 0.75 * Fnw * effective_area / 1000  # kN
            
            # Considerar el ángulo de carga
            angle_factor = sqrt((sin(radians(connection_angle)))**2 + 
                              (0.5 * cos(radians(connection_angle)))**2)
            
            adjusted_capacity = weld_capacity / angle_factor if angle_factor > 0 else weld_capacity
            
        else:  # Penetración completa
            # Soldadura de penetración completa
            effective_area = plate_thickness * weld_length  # mm²
            
            # La soldadura de penetración completa tiene la misma resistencia que el material base
            weld_capacity = 0.9 * Fy * effective_area / 1000  # kN
            adjusted_capacity = weld_capacity
        
        # Verificación por momento (si aplica)
        if M_applied > 0:
            # Módulo de sección de la soldadura
            if weld_type == "Filete":
                section_modulus = throat_thickness * weld_length**2 / 6  # mm³
            else:
                section_modulus = plate_thickness * weld_length**2 / 6  # mm³
            
            moment_stress = M_applied * 1000 / section_modulus  # MPa
            allowable_stress = 0.75 * Fnw if weld_type == "Filete" else 0.9 * Fy
            moment_utilization = moment_stress / allowable_stress
        else:
            moment_utilization = 0
        
        # Resultados
        st.subheader("📊 Resultados del Análisis")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**Propiedades de la Soldadura:**")
            if weld_type == "Filete":
                st.write(f"• Espesor de garganta: {throat_thickness:.2f} mm")
                st.write(f"• Área efectiva: {effective_area:.0f} mm²")
                st.write(f"• Resistencia del electrodo: {FEXX} MPa")
            else:
                st.write(f"• Área efectiva: {effective_area:.0f} mm²")
                st.write(f"• Resistencia: {Fy} MPa (material base)")
                
        with col4:
            st.write("**Capacidades:**")
            st.write(f"• Capacidad base: {weld_capacity:.1f} kN")
            st.write(f"• Capacidad ajustada: {adjusted_capacity:.1f} kN")
            if M_applied > 0:
                st.write(f"• Módulo de sección: {section_modulus:.0f} mm³")
        
        # Verificaciones
        st.subheader("✅ Verificaciones de Diseño")
        
        force_utilization = P_applied / adjusted_capacity
        total_utilization = sqrt(force_utilization**2 + moment_utilization**2)
        
        col5, col6, col7 = st.columns(3)
        
        with col5:
            if force_utilization <= 1.0:
                st.success(f"✅ Fuerza OK: {force_utilization:.2f}")
            else:
                st.error(f"❌ Fuerza FALLA: {force_utilization:.2f}")
        
        with col6:
            if moment_utilization <= 1.0:
                st.success(f"✅ Momento OK: {moment_utilization:.2f}")
            else:
                st.error(f"❌ Momento FALLA: {moment_utilization:.2f}")
        
        with col7:
            if total_utilization <= 1.0:
                st.success(f"✅ Total OK: {total_utilization:.2f}")
            else:
                st.error(f"❌ Total FALLA: {total_utilization:.2f}")
        
        # Gráfico de la conexión soldada
        if st.checkbox("Mostrar Gráfico de la Conexión"):
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Gráfico 1: Esquema de la soldadura
            ax1.set_xlim(0, weld_length + 40)
            ax1.set_ylim(0, 100)
            
            # Dibujar elementos
            plate1 = plt.Rectangle((20, 40), weld_length, plate_thickness, 
                                 fill=False, edgecolor='blue', linewidth=2, label='Placa')
            ax1.add_patch(plate1)
            
            # Dibujar soldadura
            if weld_type == "Filete":
                # Soldadura de filete (triángulo)
                weld_points = [(20, 40), (20, 40-weld_size), (20+weld_length, 40-weld_size), (20+weld_length, 40)]
                weld = plt.Polygon(weld_points, closed=True, fill=True, 
                                 facecolor='red', alpha=0.7, label='Soldadura')
            else:
                # Soldadura de penetración completa
                weld = plt.Rectangle((20, 35), weld_length, 5, 
                                   fill=True, facecolor='red', alpha=0.7, label='Soldadura')
            
            ax1.add_patch(weld)
            ax1.set_title(f"Esquema de Soldadura {weld_type}")
            ax1.set_xlabel("Longitud (mm)")
            ax1.set_ylabel("Altura (mm)")
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.set_aspect('equal')
            
            # Gráfico 2: Distribución de esfuerzos
            x_weld = np.linspace(0, weld_length, 100)
            
            # Esfuerzo por fuerza directa
            direct_stress = np.full_like(x_weld, P_applied * 1000 / effective_area)
            
            # Esfuerzo por momento (si aplica)
            if M_applied > 0:
                moment_stress_dist = M_applied * 1000 * (x_weld - weld_length/2) / section_modulus
                total_stress = direct_stress + moment_stress_dist
            else:
                total_stress = direct_stress
            
            ax2.plot(x_weld, direct_stress, 'b-', label='Esfuerzo Directo', linewidth=2)
            if M_applied > 0:
                ax2.plot(x_weld, moment_stress_dist, 'g--', label='Esfuerzo por Momento', linewidth=2)
                ax2.plot(x_weld, total_stress, 'r-', label='Esfuerzo Total', linewidth=3)
            
            allowable = 0.75 * Fnw if weld_type == "Filete" else 0.9 * Fy
            ax2.axhline(y=allowable, color='orange', linestyle=':', 
                       label=f'Esfuerzo Admisible ({allowable:.0f} MPa)')
            
            ax2.set_xlabel('Posición a lo largo de la soldadura (mm)')
            ax2.set_ylabel('Esfuerzo (MPa)')
            ax2.set_title('Distribución de Esfuerzos en la Soldadura')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            st.pyplot(fig)

# Información adicional
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ Información")
st.sidebar.info("""
**Códigos de Referencia:**
- AISC 360 (LRFD)
- AWS D1.1

**Factores de Resistencia:**
- Pernos: φ = 0.75
- Soldadura: φ = 0.75
- Acero: φ = 0.9

**Nota:** Este calculador es para propósitos educativos. Siempre consulte con un ingeniero estructural para aplicaciones críticas.
""")
