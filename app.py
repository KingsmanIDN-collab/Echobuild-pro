with c_exp1:
            st.subheader("📥 Impor File RAB (.xlsx / .csv)")
            uploaded_rab = st.file_uploader("Unggah file RAB Excel/CSV:", type=["xlsx", "csv"], key="rab_uploader")
            
            if uploaded_rab is not None:
                file_id = f"{uploaded_rab.name}_{uploaded_rab.size}"
                if st.session_state.get("last_uploaded_rab_id") != file_id:
                    try:
                        df_rab = pd.read_csv(uploaded_rab) if uploaded_rab.name.endswith(".csv") else pd.read_excel(uploaded_rab)
                        df_rab.columns = [str(c).strip() for c in df_rab.columns]
                        
                        col_map = {}
                        for c in df_rab.columns:
                            clow = c.lower()
                            if "material" in clow or "nama" in clow or "bahan" in clow:
                                col_map["Material"] = c
                            # Cek 'harga' TERLEBIH DAHULU sebelum 'satuan' agar 'Harga Satuan' tidak salah terdeteksi
                            elif "harga" in clow or "price" in clow or "rp" in clow:
                                col_map["Harga Satuan"] = c
                            elif "faktor" in clow or "emisi" in clow or "co2" in clow:
                                col_map["Faktor Emisi"] = c
                            elif "satuan" in clow or "unit" in clow:
                                col_map["Satuan"] = c
                            elif "jumlah" in clow or "volume" in clow or "qty" in clow:
                                col_map["Jumlah"] = c

                        if "Material" in col_map and "Jumlah" in col_map:
                            num_r = len(df_rab)
                            st.session_state["calc_num_items"] = num_r
                            st.session_state["input_num_items"] = num_r
                            
                            ice_lookup = dict(zip(df_ice_materials["Nama Material"], df_ice_materials["Faktor Emisi (kg CO2e/kg)"]))
                            
                            for idx, row in df_rab.iterrows():
                                mat_v = str(row[col_map["Material"]]).strip()
                                qty_v = float(pd.to_numeric(row[col_map["Jumlah"]], errors='coerce') or 0)
                                sat_v = str(row[col_map["Satuan"]]).strip() if "Satuan" in col_map and pd.notna(row[col_map["Satuan"]]) else "kg"
                                
                                # Ambil Faktor Emisi
                                if "Faktor Emisi" in col_map and pd.notna(row[col_map["Faktor Emisi"]]):
                                    fe_v = float(pd.to_numeric(row[col_map["Faktor Emisi"]], errors='coerce') or 1.0)
                                elif mat_v in ice_lookup:
                                    fe_v = float(ice_lookup[mat_v])
                                else:
                                    fe_v = 1.0

                                # Ambil Harga Satuan
                                if "Harga Satuan" in col_map and pd.notna(row[col_map["Harga Satuan"]]):
                                    hrg_v = float(pd.to_numeric(row[col_map["Harga Satuan"]], errors='coerce') or 10000.0)
                                else:
                                    hrg_v = 15000.0 if mat_v in ice_lookup else 10000.0

                                st.session_state[f"calc_sel_{idx}"] = "➕ Material Kustom (Isi Sendiri)"
                                st.session_state[f"c_name_{idx}"] = mat_v
                                st.session_state[f"c_unit_{idx}"] = sat_v
                                st.session_state[f"c_fact_{idx}"] = fe_v
                                st.session_state[f"c_price_{idx}"] = hrg_v
                                st.session_state[f"c_qty_{idx}"] = qty_v
                            
                            st.session_state["last_uploaded_rab_id"] = file_id
                            st.success(f"✅ Berhasil mengimpor {num_r} item material secara presisi!")
                            st.rerun()
                        else:
                            st.error("File RAB wajib memiliki minimal kolom 'Material' dan 'Jumlah'.")
                    except Exception as e:
                        st.error(f"Gagal membaca file RAB: {e}")
