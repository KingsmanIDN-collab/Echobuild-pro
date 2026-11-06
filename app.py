with c_exp1:
            st.subheader("📥 Impor File RAB (.xlsx / .csv)")
            uploaded_rab = st.file_uploader("Unggah file RAB Excel/CSV (Kolom: Material, Jumlah):", type=["xlsx", "csv"], key="rab_uploader")
            
            if uploaded_rab is not None:
                # Periksa apakah file baru diunggah
                file_id = f"{uploaded_rab.name}_{uploaded_rab.size}"
                if st.session_state.get("last_uploaded_rab") != file_id:
                    parsed_df, err_msg = smart_parse_rab_file(uploaded_rab)
                    if parsed_df is not None:
                        num_rows = len(parsed_df)
                        # 1. Update jumlah item material
                        st.session_state["calc_num_items"] = num_rows
                        st.session_state["input_num_items"] = num_rows
                        
                        ice_names = df_ice_materials["Nama Material"].tolist()
                        
                        # 2. Masukkan data RAB langsung ke widget form input
                        for i, (_, row) in enumerate(parsed_df.iterrows()):
                            mat_name = str(row["Material"]).strip()
                            qty_val = float(row["Jumlah"])
                            
                            # Cek apakah nama material ada di ICE Database
                            if mat_name in ice_names:
                                st.session_state[f"calc_sel_{i}"] = mat_name
                                st.session_state[f"q_val_{i}"] = qty_val
                            else:
                                # Jika tidak ada di ICE, jadikan Material Kustom
                                st.session_state[f"calc_sel_{i}"] = "➕ Material Kustom (Isi Sendiri)"
                                st.session_state[f"c_name_{i}"] = mat_name
                                st.session_state[f"c_qty_{i}"] = qty_val
                                st.session_state[f"c_unit_{i}"] = "kg"
                                st.session_state[f"c_fact_{i}"] = 1.0
                                st.session_state[f"c_price_{i}"] = 10000.0
                        
                        st.session_state["last_uploaded_rab"] = file_id
                        st.success(f"✅ Berhasil mengimpor {num_rows} item material dari RAB!")
                        st.rerun() # Refresh instan agar form langsung terisi
                    else:
                        st.error(err_msg)
