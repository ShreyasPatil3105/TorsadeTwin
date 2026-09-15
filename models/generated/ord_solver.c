
#include <sundials/sundials_types.h>
#include <sundials/sundials_context.h>
#include <cvode/cvode_ls.h>
#include <windows.h>

typedef sunrealtype realtype;
#define RCONST(x) ((sunrealtype)(x))
/*
ohara_rudy_cipa_v1_2017
Generated on 2026-09-16 03:49:49

Compiling on GCC:
 $ gcc -Wall -lm -lsundials_nvecserial -lsundials_cvode sim.c

Gnuplot example:
set terminal pngcairo enhanced linewidth 2 size 1200, 800;
set output 'V.png'
set size 1.0, 1.0
set xlabel 'time [ms]';
set grid
plot 'V.txt' using 1:2 with lines ls 1 title 'Vm'

*/
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include <cvode/cvode.h>
#include <nvector/nvector_serial.h>
#include <sundials/sundials_types.h>
#include <sundials/sundials_config.h>
#if SUNDIALS_VERSION_MAJOR >= 3
  #include <sunmatrix/sunmatrix_dense.h>
  #include <sunlinsol/sunlinsol_dense.h>
  
#else
  #include <cvode/cvode_dense.h>
#endif

#define N_STATE 49

/* Declare intermediary, temporary and system variables */
static realtype t;
static realtype pace;
static realtype AV_CaMKa;
static realtype AV_CaMKb;
static realtype AC_CaMKo;
static realtype AC_KmCaM;
static realtype AC_KmCaMK;
static realtype AC_aCaMK;
static realtype AC_bCaMK;
static realtype AV_A_1;
static realtype AV_A_2;
static realtype AV_A_3;
static realtype AV_Afcaf;
static realtype AV_Afcas;
static realtype AC_Aff;
static realtype AC_Afs;
static realtype AC_B_1;
static realtype AC_B_2;
static realtype AC_B_3;
static realtype AV_ICaK;
static realtype AV_ICaL_ICaL;
static realtype AV_ICaNa;
static realtype AC_Kmn;
static realtype AC_PCa;
static realtype AC_PCaK;
static realtype AC_PCaKp;
static realtype AC_PCaNa;
static realtype AC_PCaNap;
static realtype AC_PCa_b;
static realtype AC_PCap;
static realtype AV_PhiCaK;
static realtype AV_PhiCaL;
static realtype AV_PhiCaNa;
static realtype AV_U_1;
static realtype AV_U_2;
static realtype AV_U_3;
static realtype AV_anca;
static realtype AV_dss;
static realtype AV_f;
static realtype AV_fICaLp;
static realtype AV_fca;
static realtype AV_fcap;
static realtype AV_fcass;
static realtype AV_fp;
static realtype AV_fss;
static realtype AC_k2n;
static realtype AV_km2n;
static realtype AV_td;
static realtype AV_tfcaf;
static realtype AV_tfcafp;
static realtype AV_tfcas;
static realtype AV_tff;
static realtype AV_tffp;
static realtype AV_tfs;
static realtype AC_tjca;
static realtype AC_ICaL_v0;
static realtype AV_ICab_A;
static realtype AC_ICab_B;
static realtype AV_ICab_ICab;
static realtype AC_PCab;
static realtype AV_ICab_U;
static realtype AC_ICab_v0;
static realtype AC_GK1;
static realtype AC_GK1_b;
static realtype AV_IK1_IK1;
static realtype AV_rk1;
static realtype AV_txk1;
static realtype AV_xk1ss;
static realtype AC_GKb;
static realtype AC_GKb_b;
static realtype AV_IKb_IKb;
static realtype AV_xkb;
static realtype AC_A1;
static realtype AC_A11;
static realtype AC_A2;
static realtype AC_A21;
static realtype AC_A3;
static realtype AC_A31;
static realtype AC_A4;
static realtype AC_A41;
static realtype AC_A51;
static realtype AC_A52;
static realtype AC_A53;
static realtype AC_A61;
static realtype AC_A62;
static realtype AC_A63;
static realtype AC_B1;
static realtype AC_B11;
static realtype AC_B2;
static realtype AC_B21;
static realtype AC_B3;
static realtype AC_B31;
static realtype AC_B4;
static realtype AC_B41;
static realtype AC_B51;
static realtype AC_B52;
static realtype AC_B53;
static realtype AC_B61;
static realtype AC_B62;
static realtype AC_B63;
static realtype AC_GKr;
static realtype AC_GKr_b;
static realtype AV_IKr_IKr;
static realtype AC_Kmax;
static realtype AC_Kt;
static realtype AC_Ku;
static realtype AC_Temp;
static realtype AC_Vhalf;
static realtype AC_halfmax;
static realtype AC_n;
static realtype AC_q1;
static realtype AC_q11;
static realtype AC_q2;
static realtype AC_q21;
static realtype AC_q3;
static realtype AC_q31;
static realtype AC_q4;
static realtype AC_q41;
static realtype AC_q51;
static realtype AC_q52;
static realtype AC_q53;
static realtype AC_q61;
static realtype AC_q62;
static realtype AC_q63;
static realtype AC_GKs;
static realtype AC_GKs_b;
static realtype AV_IKs_IKs;
static realtype AV_KsCa;
static realtype AV_txs1;
static realtype AC_txs1_max;
static realtype AV_txs2;
static realtype AV_xs1ss;
static realtype AV_xs2ss;
static realtype AC_Ahf;
static realtype AC_Ahs;
static realtype AC_GNa;
static realtype AV_INa_INa;
static realtype AV_fINap;
static realtype AV_h;
static realtype AV_hp;
static realtype AV_hss;
static realtype AC_hssV1;
static realtype AC_hssV2;
static realtype AV_hssp;
static realtype AV_jss;
static realtype AV_mss;
static realtype AC_mssV1;
static realtype AC_mssV2;
static realtype AC_mtD1;
static realtype AC_mtD2;
static realtype AC_mtV1;
static realtype AC_mtV2;
static realtype AC_mtV3;
static realtype AC_mtV4;
static realtype AC_shift_INa_inact;
static realtype AV_thf;
static realtype AV_ths;
static realtype AV_thsp;
static realtype AV_tj;
static realtype AV_tjp;
static realtype AV_tm;
static realtype AV_E1_i;
static realtype AV_E1_ss;
static realtype AV_E2_i;
static realtype AV_E2_ss;
static realtype AV_E3_i;
static realtype AV_E3_ss;
static realtype AV_E4_i;
static realtype AV_E4_ss;
static realtype AC_Gncx;
static realtype AC_Gncx_b;
static realtype AV_INaCa_i_INaCa_i;
static realtype AV_INaCa_ss;
static realtype AV_JncxCa_i;
static realtype AV_JncxCa_ss;
static realtype AV_JncxNa_i;
static realtype AV_JncxNa_ss;
static realtype AC_KmCaAct;
static realtype AV_allo_i;
static realtype AV_allo_ss;
static realtype AC_h10_i;
static realtype AC_h10_ss;
static realtype AC_h11_i;
static realtype AC_h11_ss;
static realtype AC_h12_i;
static realtype AC_h12_ss;
static realtype AV_h1_i;
static realtype AV_h1_ss;
static realtype AV_h2_i;
static realtype AV_h2_ss;
static realtype AV_h3_i;
static realtype AV_h3_ss;
static realtype AV_h4_i;
static realtype AV_h4_ss;
static realtype AV_h5_i;
static realtype AV_h5_ss;
static realtype AV_h6_i;
static realtype AV_h6_ss;
static realtype AV_h7_i;
static realtype AV_h7_ss;
static realtype AV_h8_i;
static realtype AV_h8_ss;
static realtype AV_h9_i;
static realtype AV_h9_ss;
static realtype AV_hca;
static realtype AV_hna;
static realtype AC_k1_i;
static realtype AC_k1_ss;
static realtype AC_k2_i;
static realtype AC_k2_ss;
static realtype AV_k3_i;
static realtype AV_k3_ss;
static realtype AV_k3p_i;
static realtype AV_k3p_ss;
static realtype AV_k3pp_i;
static realtype AV_k3pp_ss;
static realtype AV_k4_i;
static realtype AV_k4_ss;
static realtype AV_k4p_i;
static realtype AV_k4p_ss;
static realtype AV_k4pp_i;
static realtype AV_k4pp_ss;
static realtype AC_k5_i;
static realtype AC_k5_ss;
static realtype AV_k6_i;
static realtype AV_k6_ss;
static realtype AV_k7_i;
static realtype AV_k7_ss;
static realtype AV_k8_i;
static realtype AV_k8_ss;
static realtype AC_kasymm;
static realtype AC_kcaoff;
static realtype AC_kcaon;
static realtype AC_kna1;
static realtype AC_kna2;
static realtype AC_kna3;
static realtype AC_qca;
static realtype AC_qna;
static realtype AC_wca;
static realtype AC_wna;
static realtype AC_wnaca;
static realtype AV_x1_i;
static realtype AV_x1_ss;
static realtype AV_x2_i;
static realtype AV_x2_ss;
static realtype AV_x3_i;
static realtype AV_x3_ss;
static realtype AV_x4_i;
static realtype AV_x4_ss;
static realtype AV_E1;
static realtype AV_E2;
static realtype AV_E3;
static realtype AV_E4;
static realtype AC_H;
static realtype AV_INaK_INaK;
static realtype AV_JnakK;
static realtype AV_JnakNa;
static realtype AC_Khp;
static realtype AC_Kki;
static realtype AC_Kko;
static realtype AC_Kmgatp;
static realtype AV_Knai;
static realtype AC_Knai0;
static realtype AV_Knao;
static realtype AC_Knao0;
static realtype AC_Knap;
static realtype AC_Kxkur;
static realtype AC_MgADP;
static realtype AC_MgATP;
static realtype AV_P;
static realtype AC_Pnak;
static realtype AC_Pnak_b;
static realtype AV_a1;
static realtype AC_a2;
static realtype AV_a3;
static realtype AC_a4;
static realtype AC_b1;
static realtype AV_b2;
static realtype AV_b3;
static realtype AV_b4;
static realtype AC_delta;
static realtype AC_eP;
static realtype AC_k1m;
static realtype AC_k1p;
static realtype AC_k2m;
static realtype AC_k2p;
static realtype AC_k3m;
static realtype AC_k3p;
static realtype AC_k4m;
static realtype AC_k4p;
static realtype AV_x1;
static realtype AV_x2;
static realtype AV_x3;
static realtype AV_x4;
static realtype AC_GNaL;
static realtype AC_GNaL_b;
static realtype AV_INaL_INaL;
static realtype AV_fINaLp;
static realtype AV_hLss;
static realtype AV_hLssp;
static realtype AV_mLss;
static realtype AC_thL;
static realtype AC_thLp;
static realtype AV_tmL;
static realtype AV_INab_A;
static realtype AC_INab_B;
static realtype AV_INab_INab;
static realtype AC_PNab;
static realtype AV_INab_U;
static realtype AC_INab_v0;
static realtype AC_GpCa;
static realtype AV_IpCa_IpCa;
static realtype AC_KmCap;
static realtype AV_AiF;
static realtype AV_AiS;
static realtype AC_Gto;
static realtype AC_Gto_b;
static realtype AV_Ito_Ito;
static realtype AV_ass;
static realtype AV_assp;
static realtype AV_delta_epi;
static realtype AV_dti_develop;
static realtype AV_dti_recover;
static realtype AV_fItop;
static realtype AV_i;
static realtype AV_ip;
static realtype AV_iss;
static realtype AV_ta;
static realtype AV_tiF;
static realtype AV_tiF_b;
static realtype AV_tiFp;
static realtype AV_tiS;
static realtype AV_tiS_b;
static realtype AV_tiSp;
static realtype AV_Jleak;
static realtype AV_Jup;
static realtype AC_Jup_b;
static realtype AV_Jupnp;
static realtype AV_Jupp;
static realtype AV_fJupp;
static realtype AC_upScale;
static realtype AC_Acap;
static realtype AC_Ageo;
static realtype AC_L;
static realtype AC_rad;
static realtype AC_vcell;
static realtype AC_vjsr;
static realtype AC_vmyo;
static realtype AC_vnsr;
static realtype AC_vss;
static realtype AV_Jdiff;
static realtype AV_JdiffK;
static realtype AV_JdiffNa;
static realtype AC_celltype;
static realtype AV_time;
static realtype AC_cao;
static realtype AC_ko;
static realtype AC_nao;
static realtype AC_BSLmax;
static realtype AC_BSRmax;
static realtype AV_Bcai;
static realtype AV_Bcajsr;
static realtype AV_Bcass;
static realtype AC_KmBSL;
static realtype AC_KmBSR;
static realtype AC_cm;
static realtype AC_cmdnmax;
static realtype AC_cmdnmax_b;
static realtype AC_csqnmax;
static realtype AC_kmcmdn;
static realtype AC_kmcsqn;
static realtype AC_kmtrpn;
static realtype AC_trpnmax;
static realtype AV_Istim;
static realtype AC_ffrt;
static realtype AC_frt;
static realtype AC_i_Stim_Amplitude;
static realtype AC_i_Stim_End;
static realtype AC_i_Stim_Period;
static realtype AC_i_Stim_PulseDuration;
static realtype AC_i_Stim_Start;
static realtype AV_vfrt;
static realtype AC_F;
static realtype AC_R;
static realtype AC_T;
static realtype AC_zca;
static realtype AC_zk;
static realtype AC_zna;
static realtype AV_EK;
static realtype AV_EKs;
static realtype AV_ENa;
static realtype AC_PKNa;
static realtype AV_Jrel;
static realtype AV_Jrel_inf;
static realtype AV_Jrel_inf_temp;
static realtype AV_Jrel_infp;
static realtype AC_Jrel_scaling_factor;
static realtype AV_Jrel_temp;
static realtype AC_a_rel;
static realtype AC_a_relp;
static realtype AC_bt;
static realtype AC_btp;
static realtype AV_fJrelp;
static realtype AV_tau_rel;
static realtype AV_tau_rel_temp;
static realtype AV_tau_relp;
static realtype AV_tau_relp_temp;
static realtype AV_Jtr;

/* Set values of constants */
static void
updateConstants(void)
{
    /* CaMK */
    AC_CaMKo = 0.05;
    AC_KmCaM = 0.0015;
    AC_KmCaMK = 0.15;
    AC_aCaMK = 0.05;
    AC_bCaMK = 0.00068;
    
    /* IpCa */
    AC_GpCa = 0.0005;
    AC_KmCap = 0.0005;
    
    /* cell_geometry */
    AC_L = 0.01;
    AC_rad = 0.0011;
    AC_Ageo = 2.0 * 3.14 * AC_rad * AC_rad + 2.0 * 3.14 * AC_rad * AC_L;
    AC_vcell = 1000.0 * 3.14 * AC_rad * AC_rad * AC_L;
    AC_Acap = 2.0 * AC_Ageo;
    AC_vjsr = 0.0048 * AC_vcell;
    AC_vmyo = 0.68 * AC_vcell;
    AC_vnsr = 0.0552 * AC_vcell;
    AC_vss = 0.02 * AC_vcell;
    
    /* environment */
    AC_celltype = 0.0;
    
    /* extracellular */
    AC_cao = 1.8;
    AC_ko = 5.4;
    AC_nao = 140.0;
    
    /* physical_constants */
    AC_F = 96485.0;
    AC_R = 8314.0;
    AC_T = 310.0;
    AC_zca = 2.0;
    AC_zk = 1.0;
    AC_zna = 1.0;
    
    /* INaCa_i */
    AC_Gncx_b = 0.0008;
    AC_KmCaAct = 0.00015;
    AC_kasymm = 12.5;
    AC_kcaoff = 5000.0;
    AC_kcaon = 1500000.0;
    AC_kna1 = 15.0;
    AC_kna2 = 5.0;
    AC_kna3 = 88.12;
    AC_qca = 0.167;
    AC_qna = 0.5224;
    AC_wca = 60000.0;
    AC_wna = 60000.0;
    AC_wnaca = 5000.0;
    AC_Gncx = ((AC_celltype == 1.0) ? AC_Gncx_b * 1.1 : ((AC_celltype == 2.0) ? AC_Gncx_b * 1.4 : AC_Gncx_b));
    AC_h10_i = AC_kasymm + 1.0 + AC_nao / AC_kna1 * (1.0 + AC_nao / AC_kna2);
    AC_h10_ss = AC_kasymm + 1.0 + AC_nao / AC_kna1 * (1.0 + AC_nao / AC_kna2);
    AC_k2_i = AC_kcaoff;
    AC_k2_ss = AC_kcaoff;
    AC_k5_i = AC_kcaoff;
    AC_k5_ss = AC_kcaoff;
    AC_h11_i = AC_nao * AC_nao / (AC_h10_i * AC_kna1 * AC_kna2);
    AC_h11_ss = AC_nao * AC_nao / (AC_h10_ss * AC_kna1 * AC_kna2);
    AC_h12_i = 1.0 / AC_h10_i;
    AC_h12_ss = 1.0 / AC_h10_ss;
    AC_k1_i = AC_h12_i * AC_cao * AC_kcaon;
    AC_k1_ss = AC_h12_ss * AC_cao * AC_kcaon;
    
    /* INaK */
    AC_H = 1e-07;
    AC_Khp = 1.698e-07;
    AC_Kki = 0.5;
    AC_Kko = 0.3582;
    AC_Kmgatp = 1.698e-07;
    AC_Knai0 = 9.073;
    AC_Knao0 = 27.78;
    AC_Knap = 224.0;
    AC_Kxkur = 292.0;
    AC_MgADP = 0.05;
    AC_MgATP = 9.8;
    AC_Pnak_b = 30.0;
    AC_delta = -0.155;
    AC_eP = 4.2;
    AC_k1m = 182.4;
    AC_k1p = 949.5;
    AC_k2m = 39.4;
    AC_k2p = 687.2;
    AC_k3m = 79300.0;
    AC_k3p = 1899.0;
    AC_k4m = 40.0;
    AC_k4p = 639.0;
    AC_Pnak = ((AC_celltype == 1.0) ? AC_Pnak_b * 0.9 : ((AC_celltype == 2.0) ? AC_Pnak_b * 0.7 : AC_Pnak_b));
    AC_a2 = AC_k2p;
    AC_a4 = AC_k4p * AC_MgATP / AC_Kmgatp / (1.0 + AC_MgATP / AC_Kmgatp);
    AC_b1 = AC_k1m * AC_MgADP;
    
    /* SERCA */
    AC_Jup_b = 1.0;
    AC_upScale = ((AC_celltype == 1.0) ? 1.3 : 1.0);
    
    /* reversal_potentials */
    AC_PKNa = 0.01833;
    
    /* IK1 */
    AC_GK1_b = 3.23978399999999778e-01;
    AC_GK1 = ((AC_celltype == 1.0) ? AC_GK1_b * 1.2 : ((AC_celltype == 2.0) ? AC_GK1_b * 1.3 : AC_GK1_b));
    
    /* IKb */
    AC_GKb_b = 0.003;
    AC_GKb = ((AC_celltype == 1.0) ? AC_GKb_b * 0.6 : AC_GKb_b);
    
    /* IKr */
    AC_A1 = 0.0264;
    AC_A11 = 0.0007868;
    AC_A2 = 4.986e-06;
    AC_A21 = 5.455e-06;
    AC_A3 = 0.001214;
    AC_A31 = 0.005509;
    AC_A4 = 1.854e-05;
    AC_A41 = 0.001416;
    AC_A51 = 0.4492;
    AC_A52 = 0.3181;
    AC_A53 = 0.149;
    AC_A61 = 0.01241;
    AC_A62 = 0.3226;
    AC_A63 = 0.008978;
    AC_B1 = 4.631e-05;
    AC_B11 = 1.535e-08;
    AC_B2 = -0.004226;
    AC_B21 = -0.1688;
    AC_B3 = 0.008516;
    AC_B31 = 7.771e-09;
    AC_B4 = -0.04641;
    AC_B41 = -0.02877;
    AC_B51 = 0.008595;
    AC_B52 = 3.613e-08;
    AC_B53 = 0.004668;
    AC_B61 = 0.1725;
    AC_B62 = -0.0006575;
    AC_B63 = -0.02215;
    AC_GKr_b = 4.65854545454545618e-02;
    AC_Kmax = 0.0;
    AC_Kt = 0.0;
    AC_Ku = 0.0;
    AC_Temp = 37.0;
    AC_Vhalf = 1.0;
    AC_halfmax = 1.0;
    AC_n = 1.0;
    AC_q1 = 4.843;
    AC_q11 = 4.942;
    AC_q2 = 4.23;
    AC_q21 = 4.156;
    AC_q3 = 4.962;
    AC_q31 = 4.22;
    AC_q4 = 3.769;
    AC_q41 = 1.459;
    AC_q51 = 5.0;
    AC_q52 = 4.663;
    AC_q53 = 2.412;
    AC_q61 = 5.568;
    AC_q62 = 5.0;
    AC_q63 = 5.682;
    AC_GKr = ((AC_celltype == 1.0) ? AC_GKr_b * 1.3 : ((AC_celltype == 2.0) ? AC_GKr_b * 0.8 : AC_GKr_b));
    
    /* IKs */
    AC_GKs_b = 6.35800000000000080e-03;
    AC_txs1_max = 817.3;
    AC_GKs = ((AC_celltype == 1.0) ? AC_GKs_b * 1.4 : AC_GKs_b);
    
    /* INa */
    AC_Ahf = 0.99;
    AC_GNa = 75.0;
    AC_hssV1 = 82.9;
    AC_hssV2 = 6.086;
    AC_mssV1 = 39.57;
    AC_mssV2 = 9.871;
    AC_mtD1 = 6.765;
    AC_mtD2 = 8.552;
    AC_mtV1 = 11.64;
    AC_mtV2 = 34.77;
    AC_mtV3 = 77.42;
    AC_mtV4 = 5.955;
    AC_shift_INa_inact = 0.0;
    AC_Ahs = 1.0 - AC_Ahf;
    
    /* Ito */
    AC_Gto_b = 0.02;
    AC_Gto = ((AC_celltype == 1.0) ? AC_Gto_b * 4.0 : ((AC_celltype == 2.0) ? AC_Gto_b * 4.0 : AC_Gto_b));
    
    /* INaL */
    AC_GNaL_b = 1.99574999999999753e-02;
    AC_thL = 200.0;
    AC_GNaL = ((AC_celltype == 1.0) ? AC_GNaL_b * 0.6 : AC_GNaL_b);
    AC_thLp = 3.0 * AC_thL;
    
    /* ICaL */
    AC_Aff = 0.6;
    AC_Kmn = 0.002;
    AC_PCa_b = 0.0001007;
    AC_k2n = 1000.0;
    AC_tjca = 75.0;
    AC_ICaL_v0 = 0.0;
    AC_Afs = 1.0 - AC_Aff;
    AC_PCa = ((AC_celltype == 1.0) ? AC_PCa_b * 1.2 : ((AC_celltype == 2.0) ? AC_PCa_b * 2.5 : AC_PCa_b));
    AC_PCaK = 0.0003574 * AC_PCa;
    AC_PCaNa = 0.00125 * AC_PCa;
    AC_PCap = 1.1 * AC_PCa;
    AC_PCaKp = 0.0003574 * AC_PCap;
    AC_PCaNap = 0.00125 * AC_PCap;
    
    /* ICab */
    AC_PCab = 2.5e-08;
    AC_ICab_v0 = 0.0;
    
    /* INab */
    AC_PNab = 3.75e-10;
    AC_INab_v0 = 0.0;
    
    /* intracellular_ions */
    AC_BSLmax = 1.124;
    AC_BSRmax = 0.047;
    AC_KmBSL = 0.0087;
    AC_KmBSR = 0.00087;
    AC_cm = 1.0;
    AC_cmdnmax_b = 0.05;
    AC_csqnmax = 10.0;
    AC_kmcmdn = 0.00238;
    AC_kmcsqn = 0.8;
    AC_kmtrpn = 0.0005;
    AC_trpnmax = 0.07;
    AC_cmdnmax = ((AC_celltype == 1.0) ? AC_cmdnmax_b * 1.3 : AC_cmdnmax_b);
    
    /* membrane */
    AC_frt = AC_F / (AC_R * AC_T);
    AC_i_Stim_Amplitude = -80.0;
    AC_i_Stim_End = 1e+17;
    AC_i_Stim_Period = 1000.0;
    AC_i_Stim_PulseDuration = 0.5;
    AC_i_Stim_Start = 10.0;
    AC_ffrt = AC_F * AC_frt;
    
    /* ryr */
    AC_Jrel_scaling_factor = 1.0;
    AC_bt = 4.75;
    AC_a_rel = 0.5 * AC_bt;
    AC_btp = 1.25 * AC_bt;
    AC_a_relp = 0.5 * AC_btp;
    
    /* *remaining* */
    AC_B_1 = 2.0 * AC_frt;
    AC_B_2 = AC_frt;
    AC_B_3 = AC_frt;
    AC_ICab_B = 2.0 * AC_frt;
    AC_INab_B = AC_frt;
    
}

/* Right-hand-side function of the model ODE */
static int rhs(realtype t, N_Vector y, N_Vector ydot, void *f_data)
{
    /* CaMK */
    AV_CaMKb = AC_CaMKo * (1.0 - NV_Ith_S(y, 1)) / (1.0 + AC_KmCaM / NV_Ith_S(y, 6));
    AV_CaMKa = AV_CaMKb + NV_Ith_S(y, 1);
    NV_Ith_S(ydot, 1) = AC_aCaMK * AV_CaMKb * (AV_CaMKb + NV_Ith_S(y, 1)) - AC_bCaMK * NV_Ith_S(y, 1);
    
    /* IpCa */
    AV_IpCa_IpCa = AC_GpCa * NV_Ith_S(y, 9) / (AC_KmCap + NV_Ith_S(y, 9));
    
    /* diff */
    AV_Jdiff = (NV_Ith_S(y, 6) - NV_Ith_S(y, 9)) / 0.2;
    AV_JdiffK = (NV_Ith_S(y, 5) - NV_Ith_S(y, 4)) / 2.0;
    AV_JdiffNa = (NV_Ith_S(y, 3) - NV_Ith_S(y, 2)) / 2.0;
    
    /* environment */
    AV_time = t;
    
    /* trans_flux */
    AV_Jtr = (NV_Ith_S(y, 7) - NV_Ith_S(y, 8)) / 100.0;
    
    /* INaCa_i */
    AV_allo_i = 1.0 / (1.0 + pow(AC_KmCaAct / NV_Ith_S(y, 9), 2.0));
    AV_allo_ss = 1.0 / (1.0 + pow(AC_KmCaAct / NV_Ith_S(y, 6), 2.0));
    AV_h4_i = 1.0 + NV_Ith_S(y, 2) / AC_kna1 * (1.0 + NV_Ith_S(y, 2) / AC_kna2);
    AV_h4_ss = 1.0 + NV_Ith_S(y, 3) / AC_kna1 * (1.0 + NV_Ith_S(y, 3) / AC_kna2);
    AV_hca = exp(AC_qca * NV_Ith_S(y, 0) * AC_F / (AC_R * AC_T));
    AV_hna = exp(AC_qna * NV_Ith_S(y, 0) * AC_F / (AC_R * AC_T));
    AV_h1_i = 1.0 + NV_Ith_S(y, 2) / AC_kna3 * (1.0 + AV_hna);
    AV_h1_ss = 1.0 + NV_Ith_S(y, 3) / AC_kna3 * (1.0 + AV_hna);
    AV_h5_i = NV_Ith_S(y, 2) * NV_Ith_S(y, 2) / (AV_h4_i * AC_kna1 * AC_kna2);
    AV_h5_ss = NV_Ith_S(y, 3) * NV_Ith_S(y, 3) / (AV_h4_ss * AC_kna1 * AC_kna2);
    AV_h6_i = 1.0 / AV_h4_i;
    AV_h6_ss = 1.0 / AV_h4_ss;
    AV_h7_i = 1.0 + AC_nao / AC_kna3 * (1.0 + 1.0 / AV_hna);
    AV_h7_ss = 1.0 + AC_nao / AC_kna3 * (1.0 + 1.0 / AV_hna);
    AV_h2_i = NV_Ith_S(y, 2) * AV_hna / (AC_kna3 * AV_h1_i);
    AV_h2_ss = NV_Ith_S(y, 3) * AV_hna / (AC_kna3 * AV_h1_ss);
    AV_h3_i = 1.0 / AV_h1_i;
    AV_h3_ss = 1.0 / AV_h1_ss;
    AV_h8_i = AC_nao / (AC_kna3 * AV_hna * AV_h7_i);
    AV_h8_ss = AC_nao / (AC_kna3 * AV_hna * AV_h7_ss);
    AV_h9_i = 1.0 / AV_h7_i;
    AV_h9_ss = 1.0 / AV_h7_ss;
    AV_k6_i = AV_h6_i * NV_Ith_S(y, 9) * AC_kcaon;
    AV_k6_ss = AV_h6_ss * NV_Ith_S(y, 6) * AC_kcaon;
    AV_k3p_i = AV_h9_i * AC_wca;
    AV_k3p_ss = AV_h9_ss * AC_wca;
    AV_k3pp_i = AV_h8_i * AC_wnaca;
    AV_k3pp_ss = AV_h8_ss * AC_wnaca;
    AV_k4p_i = AV_h3_i * AC_wca / AV_hca;
    AV_k4p_ss = AV_h3_ss * AC_wca / AV_hca;
    AV_k4pp_i = AV_h2_i * AC_wnaca;
    AV_k4pp_ss = AV_h2_ss * AC_wnaca;
    AV_k7_i = AV_h5_i * AV_h2_i * AC_wna;
    AV_k7_ss = AV_h5_ss * AV_h2_ss * AC_wna;
    AV_k8_i = AV_h8_i * AC_h11_i * AC_wna;
    AV_k8_ss = AV_h8_ss * AC_h11_ss * AC_wna;
    AV_k3_i = AV_k3p_i + AV_k3pp_i;
    AV_k3_ss = AV_k3p_ss + AV_k3pp_ss;
    AV_k4_i = AV_k4p_i + AV_k4pp_i;
    AV_k4_ss = AV_k4p_ss + AV_k4pp_ss;
    AV_x1_i = AC_k2_i * AV_k4_i * (AV_k7_i + AV_k6_i) + AC_k5_i * AV_k7_i * (AC_k2_i + AV_k3_i);
    AV_x1_ss = AC_k2_ss * AV_k4_ss * (AV_k7_ss + AV_k6_ss) + AC_k5_ss * AV_k7_ss * (AC_k2_ss + AV_k3_ss);
    AV_x2_i = AC_k1_i * AV_k7_i * (AV_k4_i + AC_k5_i) + AV_k4_i * AV_k6_i * (AC_k1_i + AV_k8_i);
    AV_x2_ss = AC_k1_ss * AV_k7_ss * (AV_k4_ss + AC_k5_ss) + AV_k4_ss * AV_k6_ss * (AC_k1_ss + AV_k8_ss);
    AV_x3_i = AC_k1_i * AV_k3_i * (AV_k7_i + AV_k6_i) + AV_k8_i * AV_k6_i * (AC_k2_i + AV_k3_i);
    AV_x3_ss = AC_k1_ss * AV_k3_ss * (AV_k7_ss + AV_k6_ss) + AV_k8_ss * AV_k6_ss * (AC_k2_ss + AV_k3_ss);
    AV_x4_i = AC_k2_i * AV_k8_i * (AV_k4_i + AC_k5_i) + AV_k3_i * AC_k5_i * (AC_k1_i + AV_k8_i);
    AV_x4_ss = AC_k2_ss * AV_k8_ss * (AV_k4_ss + AC_k5_ss) + AV_k3_ss * AC_k5_ss * (AC_k1_ss + AV_k8_ss);
    AV_E1_i = AV_x1_i / (AV_x1_i + AV_x2_i + AV_x3_i + AV_x4_i);
    AV_E1_ss = AV_x1_ss / (AV_x1_ss + AV_x2_ss + AV_x3_ss + AV_x4_ss);
    AV_E2_i = AV_x2_i / (AV_x1_i + AV_x2_i + AV_x3_i + AV_x4_i);
    AV_E2_ss = AV_x2_ss / (AV_x1_ss + AV_x2_ss + AV_x3_ss + AV_x4_ss);
    AV_E3_i = AV_x3_i / (AV_x1_i + AV_x2_i + AV_x3_i + AV_x4_i);
    AV_E3_ss = AV_x3_ss / (AV_x1_ss + AV_x2_ss + AV_x3_ss + AV_x4_ss);
    AV_E4_i = AV_x4_i / (AV_x1_i + AV_x2_i + AV_x3_i + AV_x4_i);
    AV_E4_ss = AV_x4_ss / (AV_x1_ss + AV_x2_ss + AV_x3_ss + AV_x4_ss);
    AV_JncxCa_i = AV_E2_i * AC_k2_i - AV_E1_i * AC_k1_i;
    AV_JncxCa_ss = AV_E2_ss * AC_k2_ss - AV_E1_ss * AC_k1_ss;
    AV_JncxNa_i = 3.0 * (AV_E4_i * AV_k7_i - AV_E1_i * AV_k8_i) + AV_E3_i * AV_k4pp_i - AV_E2_i * AV_k3pp_i;
    AV_JncxNa_ss = 3.0 * (AV_E4_ss * AV_k7_ss - AV_E1_ss * AV_k8_ss) + AV_E3_ss * AV_k4pp_ss - AV_E2_ss * AV_k3pp_ss;
    AV_INaCa_i_INaCa_i = 0.8 * AC_Gncx * AV_allo_i * (AC_zna * AV_JncxNa_i + AC_zca * AV_JncxCa_i);
    AV_INaCa_ss = 0.2 * AC_Gncx * AV_allo_ss * (AC_zna * AV_JncxNa_ss + AC_zca * AV_JncxCa_ss);
    
    /* INaK */
    AV_Knai = AC_Knai0 * exp(AC_delta * NV_Ith_S(y, 0) * AC_F / (3.0 * AC_R * AC_T));
    AV_Knao = AC_Knao0 * exp((1.0 - AC_delta) * NV_Ith_S(y, 0) * AC_F / (3.0 * AC_R * AC_T));
    AV_P = AC_eP / (1.0 + AC_H / AC_Khp + NV_Ith_S(y, 2) / AC_Knap + NV_Ith_S(y, 4) / AC_Kxkur);
    AV_a1 = AC_k1p * pow(NV_Ith_S(y, 2) / AV_Knai, 3.0) / (pow(1.0 + NV_Ith_S(y, 2) / AV_Knai, 3.0) + pow(1.0 + NV_Ith_S(y, 4) / AC_Kki, 2.0) - 1.0);
    AV_a3 = AC_k3p * pow(AC_ko / AC_Kko, 2.0) / (pow(1.0 + AC_nao / AV_Knao, 3.0) + pow(1.0 + AC_ko / AC_Kko, 2.0) - 1.0);
    AV_b2 = AC_k2m * pow(AC_nao / AV_Knao, 3.0) / (pow(1.0 + AC_nao / AV_Knao, 3.0) + pow(1.0 + AC_ko / AC_Kko, 2.0) - 1.0);
    AV_b3 = AC_k3m * AV_P * AC_H / (1.0 + AC_MgATP / AC_Kmgatp);
    AV_b4 = AC_k4m * pow(NV_Ith_S(y, 4) / AC_Kki, 2.0) / (pow(1.0 + NV_Ith_S(y, 2) / AV_Knai, 3.0) + pow(1.0 + NV_Ith_S(y, 4) / AC_Kki, 2.0) - 1.0);
    AV_x1 = AC_a4 * AV_a1 * AC_a2 + AV_b2 * AV_b4 * AV_b3 + AC_a2 * AV_b4 * AV_b3 + AV_b3 * AV_a1 * AC_a2;
    AV_x2 = AV_b2 * AC_b1 * AV_b4 + AV_a1 * AC_a2 * AV_a3 + AV_a3 * AC_b1 * AV_b4 + AC_a2 * AV_a3 * AV_b4;
    AV_x3 = AC_a2 * AV_a3 * AC_a4 + AV_b3 * AV_b2 * AC_b1 + AV_b2 * AC_b1 * AC_a4 + AV_a3 * AC_a4 * AC_b1;
    AV_x4 = AV_b4 * AV_b3 * AV_b2 + AV_a3 * AC_a4 * AV_a1 + AV_b2 * AC_a4 * AV_a1 + AV_b3 * AV_b2 * AV_a1;
    AV_E1 = AV_x1 / (AV_x1 + AV_x2 + AV_x3 + AV_x4);
    AV_E2 = AV_x2 / (AV_x1 + AV_x2 + AV_x3 + AV_x4);
    AV_E3 = AV_x3 / (AV_x1 + AV_x2 + AV_x3 + AV_x4);
    AV_E4 = AV_x4 / (AV_x1 + AV_x2 + AV_x3 + AV_x4);
    AV_JnakK = 2.0 * (AV_E4 * AC_b1 - AV_E3 * AV_a1);
    AV_JnakNa = 3.0 * (AV_E1 * AV_a3 - AV_E2 * AV_b3);
    AV_INaK_INaK = AC_Pnak * (AC_zna * AV_JnakNa + AC_zk * AV_JnakK);
    
    /* SERCA */
    AV_Jleak = 0.0039375 * NV_Ith_S(y, 7) / 15.0;
    AV_fJupp = 1.0 / (1.0 + AC_KmCaMK / AV_CaMKa);
    AV_Jupnp = AC_upScale * 0.004375 * NV_Ith_S(y, 9) / (NV_Ith_S(y, 9) + 0.00092);
    AV_Jupp = AC_upScale * 2.75 * 0.004375 * NV_Ith_S(y, 9) / (NV_Ith_S(y, 9) + 0.00092 - 0.00017);
    AV_Jup = AC_Jup_b * ((1.0 - AV_fJupp) * AV_Jupnp + AV_fJupp * AV_Jupp - AV_Jleak);
    
    /* reversal_potentials */
    AV_EK = AC_R * AC_T / AC_F * log(AC_ko / NV_Ith_S(y, 4));
    AV_ENa = AC_R * AC_T / AC_F * log(AC_nao / NV_Ith_S(y, 2));
    AV_EKs = AC_R * AC_T / AC_F * log((AC_ko + AC_PKNa * AC_nao) / (NV_Ith_S(y, 4) + AC_PKNa * NV_Ith_S(y, 2)));
    
    /* IK1 */
    AV_rk1 = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) + 105.8 - 2.6 * AC_ko) / 9.493));
    AV_txk1 = 122.2 / (exp(-(NV_Ith_S(y, 0) + 127.2) / 20.36) + exp((NV_Ith_S(y, 0) + 236.8) / 69.33));
    AV_xk1ss = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) + 2.5538 * AC_ko + 144.59) / (1.5692 * AC_ko + 3.8115)));
    NV_Ith_S(ydot, 46) = (AV_xk1ss - NV_Ith_S(y, 46)) / AV_txk1;
    AV_IK1_IK1 = AC_GK1 * sqrt(AC_ko) * AV_rk1 * NV_Ith_S(y, 46) * (NV_Ith_S(y, 0) - AV_EK);
    
    /* IKb */
    AV_xkb = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) - 14.48) / 18.34));
    AV_IKb_IKb = AC_GKb * AV_xkb * (NV_Ith_S(y, 0) - AV_EK);
    
    /* IKr */
    NV_Ith_S(ydot, 43) = 0.0;
    NV_Ith_S(ydot, 36) = -(AC_A1 * exp(AC_B1 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 36) * exp((AC_Temp - 20.0) * log(AC_q1) / 10.0) - AC_A2 * exp(AC_B2 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 37) * exp((AC_Temp - 20.0) * log(AC_q2) / 10.0)) - (AC_A51 * exp(AC_B51 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 36) * exp((AC_Temp - 20.0) * log(AC_q51) / 10.0) - AC_A61 * exp(AC_B61 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 34) * exp((AC_Temp - 20.0) * log(AC_q61) / 10.0));
    NV_Ith_S(ydot, 37) = AC_A1 * exp(AC_B1 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 36) * exp((AC_Temp - 20.0) * log(AC_q1) / 10.0) - AC_A2 * exp(AC_B2 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 37) * exp((AC_Temp - 20.0) * log(AC_q2) / 10.0) - (AC_A31 * exp(AC_B31 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 37) * exp((AC_Temp - 20.0) * log(AC_q31) / 10.0) - AC_A41 * exp(AC_B41 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 38) * exp((AC_Temp - 20.0) * log(AC_q41) / 10.0)) - (AC_A52 * exp(AC_B52 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 37) * exp((AC_Temp - 20.0) * log(AC_q52) / 10.0) - AC_A62 * exp(AC_B62 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 35) * exp((AC_Temp - 20.0) * log(AC_q62) / 10.0));
    NV_Ith_S(ydot, 42) = -(AC_Kt / (1.0 + exp(-(NV_Ith_S(y, 0) - AC_Vhalf) / 6.789)) * NV_Ith_S(y, 42) - AC_Kt * NV_Ith_S(y, 41)) - (AC_Kt / (1.0 + exp(-(NV_Ith_S(y, 0) - AC_Vhalf) / 6.789)) * NV_Ith_S(y, 42) - AC_Kt * NV_Ith_S(y, 40));
    NV_Ith_S(ydot, 34) = -(AC_A11 * exp(AC_B11 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 34) * exp((AC_Temp - 20.0) * log(AC_q11) / 10.0) - AC_A21 * exp(AC_B21 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 35) * exp((AC_Temp - 20.0) * log(AC_q21) / 10.0)) + AC_A51 * exp(AC_B51 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 36) * exp((AC_Temp - 20.0) * log(AC_q51) / 10.0) - AC_A61 * exp(AC_B61 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 34) * exp((AC_Temp - 20.0) * log(AC_q61) / 10.0);
    NV_Ith_S(ydot, 35) = AC_A11 * exp(AC_B11 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 34) * exp((AC_Temp - 20.0) * log(AC_q11) / 10.0) - AC_A21 * exp(AC_B21 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 35) * exp((AC_Temp - 20.0) * log(AC_q21) / 10.0) - (AC_A3 * exp(AC_B3 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 35) * exp((AC_Temp - 20.0) * log(AC_q3) / 10.0) - AC_A4 * exp(AC_B4 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 39) * exp((AC_Temp - 20.0) * log(AC_q4) / 10.0)) + AC_A52 * exp(AC_B52 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 37) * exp((AC_Temp - 20.0) * log(AC_q52) / 10.0) - AC_A62 * exp(AC_B62 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 35) * exp((AC_Temp - 20.0) * log(AC_q62) / 10.0);
    NV_Ith_S(ydot, 39) = AC_A3 * exp(AC_B3 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 35) * exp((AC_Temp - 20.0) * log(AC_q3) / 10.0) - AC_A4 * exp(AC_B4 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 39) * exp((AC_Temp - 20.0) * log(AC_q4) / 10.0) + AC_A53 * exp(AC_B53 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 38) * exp((AC_Temp - 20.0) * log(AC_q53) / 10.0) - AC_A63 * exp(AC_B63 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 39) * exp((AC_Temp - 20.0) * log(AC_q63) / 10.0) - (AC_Kmax * AC_Ku * exp(AC_n * log(NV_Ith_S(y, 43))) / (exp(AC_n * log(NV_Ith_S(y, 43))) + AC_halfmax) * NV_Ith_S(y, 39) - AC_Ku * AC_A53 * exp(AC_B53 * NV_Ith_S(y, 0)) * exp((AC_Temp - 20.0) * log(AC_q53) / 10.0) / (AC_A63 * exp(AC_B63 * NV_Ith_S(y, 0)) * exp((AC_Temp - 20.0) * log(AC_q63) / 10.0)) * NV_Ith_S(y, 40));
    NV_Ith_S(ydot, 40) = AC_Kmax * AC_Ku * exp(AC_n * log(NV_Ith_S(y, 43))) / (exp(AC_n * log(NV_Ith_S(y, 43))) + AC_halfmax) * NV_Ith_S(y, 39) - AC_Ku * AC_A53 * exp(AC_B53 * NV_Ith_S(y, 0)) * exp((AC_Temp - 20.0) * log(AC_q53) / 10.0) / (AC_A63 * exp(AC_B63 * NV_Ith_S(y, 0)) * exp((AC_Temp - 20.0) * log(AC_q63) / 10.0)) * NV_Ith_S(y, 40) + AC_Kt / (1.0 + exp(-(NV_Ith_S(y, 0) - AC_Vhalf) / 6.789)) * NV_Ith_S(y, 42) - AC_Kt * NV_Ith_S(y, 40);
    NV_Ith_S(ydot, 38) = AC_A31 * exp(AC_B31 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 37) * exp((AC_Temp - 20.0) * log(AC_q31) / 10.0) - AC_A41 * exp(AC_B41 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 38) * exp((AC_Temp - 20.0) * log(AC_q41) / 10.0) - (AC_A53 * exp(AC_B53 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 38) * exp((AC_Temp - 20.0) * log(AC_q53) / 10.0) - AC_A63 * exp(AC_B63 * NV_Ith_S(y, 0)) * NV_Ith_S(y, 39) * exp((AC_Temp - 20.0) * log(AC_q63) / 10.0)) - (AC_Kmax * AC_Ku * exp(AC_n * log(NV_Ith_S(y, 43))) / (exp(AC_n * log(NV_Ith_S(y, 43))) + AC_halfmax) * NV_Ith_S(y, 38) - AC_Ku * NV_Ith_S(y, 41));
    NV_Ith_S(ydot, 41) = AC_Kmax * AC_Ku * exp(AC_n * log(NV_Ith_S(y, 43))) / (exp(AC_n * log(NV_Ith_S(y, 43))) + AC_halfmax) * NV_Ith_S(y, 38) - AC_Ku * NV_Ith_S(y, 41) + AC_Kt / (1.0 + exp(-(NV_Ith_S(y, 0) - AC_Vhalf) / 6.789)) * NV_Ith_S(y, 42) - AC_Kt * NV_Ith_S(y, 41);
    AV_IKr_IKr = AC_GKr * sqrt(AC_ko / 5.4) * NV_Ith_S(y, 38) * (NV_Ith_S(y, 0) - AV_EK);
    
    /* IKs */
    AV_KsCa = 1.0 + 0.6 / (1.0 + pow(3.8e-05 / NV_Ith_S(y, 9), 1.4));
    AV_txs2 = 1.0 / (0.01 * exp((NV_Ith_S(y, 0) - 50.0) / 20.0) + 0.0193 * exp(-(NV_Ith_S(y, 0) + 66.54) / 31.0));
    AV_xs1ss = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) + 11.6) / 8.932));
    AV_txs1 = AC_txs1_max + 1.0 / (0.0002326 * exp((NV_Ith_S(y, 0) + 48.28) / 17.8) + 0.001292 * exp(-(NV_Ith_S(y, 0) + 210.0) / 230.0));
    AV_xs2ss = AV_xs1ss;
    AV_IKs_IKs = AC_GKs * AV_KsCa * NV_Ith_S(y, 44) * NV_Ith_S(y, 45) * (NV_Ith_S(y, 0) - AV_EKs);
    NV_Ith_S(ydot, 44) = (AV_xs1ss - NV_Ith_S(y, 44)) / AV_txs1;
    NV_Ith_S(ydot, 45) = (AV_xs2ss - NV_Ith_S(y, 45)) / AV_txs2;
    
    /* INa */
    AV_fINap = 1.0 / (1.0 + AC_KmCaMK / AV_CaMKa);
    AV_hss = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) + AC_hssV1 - AC_shift_INa_inact) / AC_hssV2));
    AV_hssp = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) + 89.1 - AC_shift_INa_inact) / 6.086));
    AV_mss = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) + AC_mssV1) / AC_mssV2));
    AV_thf = 1.0 / (1.432e-05 * exp(-(NV_Ith_S(y, 0) + 1.196 - AC_shift_INa_inact) / 6.285) + 6.149 * exp((NV_Ith_S(y, 0) + 0.5096 - AC_shift_INa_inact) / 20.27));
    AV_ths = 1.0 / (0.009794 * exp(-(NV_Ith_S(y, 0) + 17.95 - AC_shift_INa_inact) / 28.05) + 0.3343 * exp((NV_Ith_S(y, 0) + 5.73 - AC_shift_INa_inact) / 56.66));
    AV_tj = 2.038 + 1.0 / (0.02136 * exp(-(NV_Ith_S(y, 0) + 100.6 - AC_shift_INa_inact) / 8.281) + 0.3052 * exp((NV_Ith_S(y, 0) + 0.9941 - AC_shift_INa_inact) / 38.45));
    AV_tm = 1.0 / (AC_mtD1 * exp((NV_Ith_S(y, 0) + AC_mtV1) / AC_mtV2) + AC_mtD2 * exp(-(NV_Ith_S(y, 0) + AC_mtV3) / AC_mtV4));
    AV_h = AC_Ahf * NV_Ith_S(y, 11) + AC_Ahs * NV_Ith_S(y, 12);
    AV_hp = AC_Ahf * NV_Ith_S(y, 11) + AC_Ahs * NV_Ith_S(y, 14);
    AV_jss = AV_hss;
    AV_thsp = 3.0 * AV_ths;
    AV_tjp = 1.46 * AV_tj;
    NV_Ith_S(ydot, 11) = (AV_hss - NV_Ith_S(y, 11)) / AV_thf;
    NV_Ith_S(ydot, 12) = (AV_hss - NV_Ith_S(y, 12)) / AV_ths;
    NV_Ith_S(ydot, 10) = (AV_mss - NV_Ith_S(y, 10)) / AV_tm;
    AV_INa_INa = AC_GNa * (NV_Ith_S(y, 0) - AV_ENa) * pow(NV_Ith_S(y, 10), 3.0) * ((1.0 - AV_fINap) * AV_h * NV_Ith_S(y, 13) + AV_fINap * AV_hp * NV_Ith_S(y, 15));
    NV_Ith_S(ydot, 14) = (AV_hssp - NV_Ith_S(y, 14)) / AV_thsp;
    NV_Ith_S(ydot, 13) = (AV_jss - NV_Ith_S(y, 13)) / AV_tj;
    NV_Ith_S(ydot, 15) = (AV_jss - NV_Ith_S(y, 15)) / AV_tjp;
    
    /* Ito */
    AV_AiF = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) - 213.6) / 151.2));
    AV_ass = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) - 14.34) / 14.82));
    AV_assp = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) - 24.34) / 14.82));
    AV_delta_epi = ((AC_celltype == 1.0) ? 1.0 - 0.95 / (1.0 + exp((NV_Ith_S(y, 0) + 70.0) / 5.0)) : 1.0);
    AV_dti_develop = 1.354 + 0.0001 / (exp((NV_Ith_S(y, 0) - 167.4) / 15.89) + exp(-(NV_Ith_S(y, 0) - 12.23) / 0.2154));
    AV_dti_recover = 1.0 - 0.5 / (1.0 + exp((NV_Ith_S(y, 0) + 70.0) / 20.0));
    AV_fItop = 1.0 / (1.0 + AC_KmCaMK / AV_CaMKa);
    AV_iss = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) + 43.94) / 5.711));
    AV_ta = 1.0515 / (1.0 / (1.2089 * (1.0 + exp(-(NV_Ith_S(y, 0) - 18.4099) / 29.3814))) + 3.5 / (1.0 + exp((NV_Ith_S(y, 0) + 100.0) / 29.3814)));
    AV_tiF_b = 4.562 + 1.0 / (0.3933 * exp(-(NV_Ith_S(y, 0) + 100.0) / 100.0) + 0.08004 * exp((NV_Ith_S(y, 0) + 50.0) / 16.59));
    AV_tiS_b = 23.62 + 1.0 / (0.001416 * exp(-(NV_Ith_S(y, 0) + 96.52) / 59.05) + 1.78e-08 * exp((NV_Ith_S(y, 0) + 114.1) / 8.079));
    AV_AiS = 1.0 - AV_AiF;
    AV_tiF = AV_tiF_b * AV_delta_epi;
    AV_tiS = AV_tiS_b * AV_delta_epi;
    NV_Ith_S(ydot, 19) = (AV_ass - NV_Ith_S(y, 19)) / AV_ta;
    NV_Ith_S(ydot, 22) = (AV_assp - NV_Ith_S(y, 22)) / AV_ta;
    AV_i = AV_AiF * NV_Ith_S(y, 20) + AV_AiS * NV_Ith_S(y, 21);
    AV_ip = AV_AiF * NV_Ith_S(y, 23) + AV_AiS * NV_Ith_S(y, 24);
    AV_tiFp = AV_dti_develop * AV_dti_recover * AV_tiF;
    AV_tiSp = AV_dti_develop * AV_dti_recover * AV_tiS;
    NV_Ith_S(ydot, 20) = (AV_iss - NV_Ith_S(y, 20)) / AV_tiF;
    NV_Ith_S(ydot, 21) = (AV_iss - NV_Ith_S(y, 21)) / AV_tiS;
    AV_Ito_Ito = AC_Gto * (NV_Ith_S(y, 0) - AV_EK) * ((1.0 - AV_fItop) * NV_Ith_S(y, 19) * AV_i + AV_fItop * NV_Ith_S(y, 22) * AV_ip);
    NV_Ith_S(ydot, 23) = (AV_iss - NV_Ith_S(y, 23)) / AV_tiFp;
    NV_Ith_S(ydot, 24) = (AV_iss - NV_Ith_S(y, 24)) / AV_tiSp;
    
    /* INaL */
    AV_fINaLp = 1.0 / (1.0 + AC_KmCaMK / AV_CaMKa);
    AV_hLss = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) + 87.61) / 7.488));
    AV_hLssp = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) + 93.81) / 7.488));
    AV_mLss = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) + 42.85) / 5.264));
    AV_tmL = AV_tm;
    NV_Ith_S(ydot, 17) = (AV_hLss - NV_Ith_S(y, 17)) / AC_thL;
    NV_Ith_S(ydot, 16) = (AV_mLss - NV_Ith_S(y, 16)) / AV_tmL;
    AV_INaL_INaL = AC_GNaL * (NV_Ith_S(y, 0) - AV_ENa) * NV_Ith_S(y, 16) * ((1.0 - AV_fINaLp) * NV_Ith_S(y, 17) + AV_fINaLp * NV_Ith_S(y, 18));
    NV_Ith_S(ydot, 18) = (AV_hLssp - NV_Ith_S(y, 18)) / AC_thLp;
    
    /* ICaL */
    AV_Afcaf = 0.3 + 0.6 / (1.0 + exp((NV_Ith_S(y, 0) - 10.0) / 10.0));
    AV_dss = 1.0 / (1.0 + exp(-(NV_Ith_S(y, 0) + 3.94) / 4.23));
    AV_fICaLp = 1.0 / (1.0 + AC_KmCaMK / AV_CaMKa);
    AV_fss = 1.0 / (1.0 + exp((NV_Ith_S(y, 0) + 19.58) / 3.696));
    AV_km2n = NV_Ith_S(y, 30) * 1.0;
    AV_td = 0.6 + 1.0 / (exp(-0.05 * (NV_Ith_S(y, 0) + 6.0)) + exp(0.09 * (NV_Ith_S(y, 0) + 14.0)));
    AV_tfcaf = 7.0 + 1.0 / (0.04 * exp(-(NV_Ith_S(y, 0) - 4.0) / 7.0) + 0.04 * exp((NV_Ith_S(y, 0) - 4.0) / 7.0));
    AV_tfcas = 100.0 + 1.0 / (0.00012 * exp(-NV_Ith_S(y, 0) / 3.0) + 0.00012 * exp(NV_Ith_S(y, 0) / 7.0));
    AV_tff = 7.0 + 1.0 / (0.0045 * exp(-(NV_Ith_S(y, 0) + 20.0) / 10.0) + 0.0045 * exp((NV_Ith_S(y, 0) + 20.0) / 10.0));
    AV_tfs = 1000.0 + 1.0 / (3.5e-05 * exp(-(NV_Ith_S(y, 0) + 5.0) / 4.0) + 3.5e-05 * exp((NV_Ith_S(y, 0) + 5.0) / 6.0));
    AV_Afcas = 1.0 - AV_Afcaf;
    AV_anca = 1.0 / (AC_k2n / AV_km2n + pow(1.0 + AC_Kmn / NV_Ith_S(y, 6), 4.0));
    AV_fcass = AV_fss;
    AV_tfcafp = 2.5 * AV_tfcaf;
    AV_tffp = 2.5 * AV_tff;
    NV_Ith_S(ydot, 25) = (AV_dss - NV_Ith_S(y, 25)) / AV_td;
    NV_Ith_S(ydot, 26) = (AV_fss - NV_Ith_S(y, 26)) / AV_tff;
    NV_Ith_S(ydot, 27) = (AV_fss - NV_Ith_S(y, 27)) / AV_tfs;
    AV_f = AC_Aff * NV_Ith_S(y, 26) + AC_Afs * NV_Ith_S(y, 27);
    AV_fca = AV_Afcaf * NV_Ith_S(y, 28) + AV_Afcas * NV_Ith_S(y, 29);
    AV_fcap = AV_Afcaf * NV_Ith_S(y, 32) + AV_Afcas * NV_Ith_S(y, 29);
    AV_fp = AC_Aff * NV_Ith_S(y, 31) + AC_Afs * NV_Ith_S(y, 27);
    NV_Ith_S(ydot, 28) = (AV_fcass - NV_Ith_S(y, 28)) / AV_tfcaf;
    NV_Ith_S(ydot, 32) = (AV_fcass - NV_Ith_S(y, 32)) / AV_tfcafp;
    NV_Ith_S(ydot, 29) = (AV_fcass - NV_Ith_S(y, 29)) / AV_tfcas;
    NV_Ith_S(ydot, 31) = (AV_fss - NV_Ith_S(y, 31)) / AV_tffp;
    NV_Ith_S(ydot, 30) = (AV_fcass - NV_Ith_S(y, 30)) / AC_tjca;
    NV_Ith_S(ydot, 33) = AV_anca * AC_k2n - NV_Ith_S(y, 33) * AV_km2n;
    
    /* intracellular_ions */
    NV_Ith_S(ydot, 7) = AV_Jup - AV_Jtr * AC_vjsr / AC_vnsr;
    AV_Bcajsr = 1.0 / (1.0 + AC_csqnmax * AC_kmcsqn / pow(AC_kmcsqn + NV_Ith_S(y, 8), 2.0));
    AV_Bcass = 1.0 / (1.0 + AC_BSRmax * AC_KmBSR / pow(AC_KmBSR + NV_Ith_S(y, 6), 2.0) + AC_BSLmax * AC_KmBSL / pow(AC_KmBSL + NV_Ith_S(y, 6), 2.0));
    AV_Bcai = 1.0 / (1.0 + AC_cmdnmax * AC_kmcmdn / pow(AC_kmcmdn + NV_Ith_S(y, 9), 2.0) + AC_trpnmax * AC_kmtrpn / pow(AC_kmtrpn + NV_Ith_S(y, 9), 2.0));
    
    /* membrane */
    AV_Istim = ((((AV_time >= AC_i_Stim_Start) && (AV_time <= AC_i_Stim_End)) && (AV_time - AC_i_Stim_Start - floor((AV_time - AC_i_Stim_Start) / AC_i_Stim_Period) * AC_i_Stim_Period <= AC_i_Stim_PulseDuration)) ? AC_i_Stim_Amplitude : 0.0);
    AV_vfrt = NV_Ith_S(y, 0) * AC_frt;
    
    /* ryr */
    AV_fJrelp = 1.0 / (1.0 + AC_KmCaMK / AV_CaMKa);
    AV_Jrel = AC_Jrel_scaling_factor * ((1.0 - AV_fJrelp) * NV_Ith_S(y, 47) + AV_fJrelp * NV_Ith_S(y, 48));
    AV_tau_rel_temp = AC_bt / (1.0 + 0.0123 / NV_Ith_S(y, 8));
    AV_tau_rel = ((AV_tau_rel_temp < 0.001) ? 0.001 : AV_tau_rel_temp);
    AV_tau_relp_temp = AC_btp / (1.0 + 0.0123 / NV_Ith_S(y, 8));
    AV_tau_relp = ((AV_tau_relp_temp < 0.001) ? 0.001 : AV_tau_relp_temp);
    
    /* *remaining* */
    NV_Ith_S(ydot, 8) = AV_Bcajsr * (AV_Jtr - AV_Jrel);
    NV_Ith_S(ydot, 4) = -(AV_Ito_Ito + AV_IKr_IKr + AV_IKs_IKs + AV_IK1_IK1 + AV_IKb_IKb + AV_Istim - 2.0 * AV_INaK_INaK) * AC_cm * AC_Acap / (AC_F * AC_vmyo) + AV_JdiffK * AC_vss / AC_vmyo;
    AV_A_1 = 4.0 * AC_ffrt * (NV_Ith_S(y, 6) * exp(2.0 * AV_vfrt) - 0.341 * AC_cao) / AC_B_1;
    AV_A_2 = 0.75 * AC_ffrt * (NV_Ith_S(y, 3) * exp(AV_vfrt) - AC_nao) / AC_B_2;
    AV_A_3 = 0.75 * AC_ffrt * (NV_Ith_S(y, 5) * exp(AV_vfrt) - AC_ko) / AC_B_3;
    AV_U_1 = AC_B_1 * (NV_Ith_S(y, 0) - AC_ICaL_v0);
    AV_U_2 = AC_B_2 * (NV_Ith_S(y, 0) - AC_ICaL_v0);
    AV_U_3 = AC_B_3 * (NV_Ith_S(y, 0) - AC_ICaL_v0);
    AV_ICab_A = AC_PCab * 4.0 * AC_ffrt * (NV_Ith_S(y, 9) * exp(2.0 * AV_vfrt) - 0.341 * AC_cao) / AC_ICab_B;
    AV_ICab_U = AC_ICab_B * (NV_Ith_S(y, 0) - AC_ICab_v0);
    AV_INab_A = AC_PNab * AC_ffrt * (NV_Ith_S(y, 2) * exp(AV_vfrt) - AC_nao) / AC_INab_B;
    AV_INab_U = AC_INab_B * (NV_Ith_S(y, 0) - AC_INab_v0);
    AV_PhiCaK = (((-1e-07 <= AV_U_3) && (AV_U_3 <= 1e-07)) ? AV_A_3 * (1.0 - 0.5 * AV_U_3) : AV_A_3 * AV_U_3 / (exp(AV_U_3) - 1.0));
    AV_PhiCaL = (((-1e-07 <= AV_U_1) && (AV_U_1 <= 1e-07)) ? AV_A_1 * (1.0 - 0.5 * AV_U_1) : AV_A_1 * AV_U_1 / (exp(AV_U_1) - 1.0));
    AV_PhiCaNa = (((-1e-07 <= AV_U_2) && (AV_U_2 <= 1e-07)) ? AV_A_2 * (1.0 - 0.5 * AV_U_2) : AV_A_2 * AV_U_2 / (exp(AV_U_2) - 1.0));
    AV_ICab_ICab = (((-1e-07 <= AV_ICab_U) && (AV_ICab_U <= 1e-07)) ? AV_ICab_A * (1.0 - 0.5 * AV_ICab_U) : AV_ICab_A * AV_ICab_U / (exp(AV_ICab_U) - 1.0));
    AV_INab_INab = (((-1e-07 <= AV_INab_U) && (AV_INab_U <= 1e-07)) ? AV_INab_A * (1.0 - 0.5 * AV_INab_U) : AV_INab_A * AV_INab_U / (exp(AV_INab_U) - 1.0));
    AV_ICaK = (1.0 - AV_fICaLp) * AC_PCaK * AV_PhiCaK * NV_Ith_S(y, 25) * (AV_f * (1.0 - NV_Ith_S(y, 33)) + NV_Ith_S(y, 30) * AV_fca * NV_Ith_S(y, 33)) + AV_fICaLp * AC_PCaKp * AV_PhiCaK * NV_Ith_S(y, 25) * (AV_fp * (1.0 - NV_Ith_S(y, 33)) + NV_Ith_S(y, 30) * AV_fcap * NV_Ith_S(y, 33));
    AV_ICaL_ICaL = (1.0 - AV_fICaLp) * AC_PCa * AV_PhiCaL * NV_Ith_S(y, 25) * (AV_f * (1.0 - NV_Ith_S(y, 33)) + NV_Ith_S(y, 30) * AV_fca * NV_Ith_S(y, 33)) + AV_fICaLp * AC_PCap * AV_PhiCaL * NV_Ith_S(y, 25) * (AV_fp * (1.0 - NV_Ith_S(y, 33)) + NV_Ith_S(y, 30) * AV_fcap * NV_Ith_S(y, 33));
    AV_ICaNa = (1.0 - AV_fICaLp) * AC_PCaNa * AV_PhiCaNa * NV_Ith_S(y, 25) * (AV_f * (1.0 - NV_Ith_S(y, 33)) + NV_Ith_S(y, 30) * AV_fca * NV_Ith_S(y, 33)) + AV_fICaLp * AC_PCaNap * AV_PhiCaNa * NV_Ith_S(y, 25) * (AV_fp * (1.0 - NV_Ith_S(y, 33)) + NV_Ith_S(y, 30) * AV_fcap * NV_Ith_S(y, 33));
    NV_Ith_S(ydot, 9) = AV_Bcai * (-(AV_IpCa_IpCa + AV_ICab_ICab - 2.0 * AV_INaCa_i_INaCa_i) * AC_cm * AC_Acap / (2.0 * AC_F * AC_vmyo) - AV_Jup * AC_vnsr / AC_vmyo + AV_Jdiff * AC_vss / AC_vmyo);
    NV_Ith_S(ydot, 2) = -(AV_INa_INa + AV_INaL_INaL + 3.0 * AV_INaCa_i_INaCa_i + 3.0 * AV_INaK_INaK + AV_INab_INab) * AC_Acap * AC_cm / (AC_F * AC_vmyo) + AV_JdiffNa * AC_vss / AC_vmyo;
    NV_Ith_S(ydot, 6) = AV_Bcass * (-(AV_ICaL_ICaL - 2.0 * AV_INaCa_ss) * AC_cm * AC_Acap / (2.0 * AC_F * AC_vss) + AV_Jrel * AC_vjsr / AC_vss - AV_Jdiff);
    NV_Ith_S(ydot, 5) = -AV_ICaK * AC_cm * AC_Acap / (AC_F * AC_vss) - AV_JdiffK;
    NV_Ith_S(ydot, 3) = -(AV_ICaNa + 3.0 * AV_INaCa_ss) * AC_cm * AC_Acap / (AC_F * AC_vss) - AV_JdiffNa;
    NV_Ith_S(ydot, 0) = -(AV_INa_INa + AV_INaL_INaL + AV_Ito_Ito + AV_ICaL_ICaL + AV_ICaNa + AV_ICaK + AV_IKr_IKr + AV_IKs_IKs + AV_IK1_IK1 + AV_INaCa_i_INaCa_i + AV_INaCa_ss + AV_INaK_INaK + AV_INab_INab + AV_IKb_IKb + AV_IpCa_IpCa + AV_ICab_ICab + AV_Istim);
    AV_Jrel_inf_temp = AC_a_rel * -AV_ICaL_ICaL / (1.0 + 1.0 * pow(1.5 / NV_Ith_S(y, 8), 8.0));
    AV_Jrel_temp = AC_a_relp * -AV_ICaL_ICaL / (1.0 + pow(1.5 / NV_Ith_S(y, 8), 8.0));
    AV_Jrel_inf = ((AC_celltype == 2.0) ? AV_Jrel_inf_temp * 1.7 : AV_Jrel_inf_temp);
    AV_Jrel_infp = ((AC_celltype == 2.0) ? AV_Jrel_temp * 1.7 : AV_Jrel_temp);
    NV_Ith_S(ydot, 47) = (AV_Jrel_inf - NV_Ith_S(y, 47)) / AV_tau_rel;
    NV_Ith_S(ydot, 48) = (AV_Jrel_infp - NV_Ith_S(y, 48)) / AV_tau_relp;
    

    return 0;
}

/* Set initial values */
static void
default_initial_values(N_Vector y)
{
    NV_Ith_S(y, 0) = -8.80019046500000002e+01;
    NV_Ith_S(y, 1) =  1.25840446999999998e-02;
    NV_Ith_S(y, 2) =  7.26800449799999981e+00;
    NV_Ith_S(y, 3) =  7.26808997699999981e+00;
    NV_Ith_S(y, 4) =  1.44655591799999996e+02;
    NV_Ith_S(y, 5) =  1.44655565099999990e+02;
    NV_Ith_S(y, 6) = 8.49e-05;
    NV_Ith_S(y, 7) =  1.61957453799999995e+00;
    NV_Ith_S(y, 8) =  1.57123401400000007e+00;
    NV_Ith_S(y, 9) = 8.6e-05;
    NV_Ith_S(y, 10) =  7.34412110199999992e-03;
    NV_Ith_S(y, 11) =  6.98107191299999985e-01;
    NV_Ith_S(y, 12) =  6.98089580099999996e-01;
    NV_Ith_S(y, 13) =  6.97990843200000044e-01;
    NV_Ith_S(y, 14) =  4.54948552499999992e-01;
    NV_Ith_S(y, 15) =  6.97924586499999999e-01;
    NV_Ith_S(y, 16) =  1.88261727299999989e-04;
    NV_Ith_S(y, 17) =  5.00854885500000013e-01;
    NV_Ith_S(y, 18) =  2.69306535700000016e-01;
    NV_Ith_S(y, 19) =  1.00109768699999991e-03;
    NV_Ith_S(y, 20) =  9.99554174499999948e-01;
    NV_Ith_S(y, 21) =  5.86506173600000014e-01;
    NV_Ith_S(y, 22) =  5.10086293400000023e-04;
    NV_Ith_S(y, 23) =  9.99554182300000038e-01;
    NV_Ith_S(y, 24) =  6.39339948199999952e-01;
    NV_Ith_S(y, 25) = 2.34e-09;
    NV_Ith_S(y, 26) =  9.99999990900000024e-01;
    NV_Ith_S(y, 27) =  9.10241277699999962e-01;
    NV_Ith_S(y, 28) =  9.99999990900000024e-01;
    NV_Ith_S(y, 29) =  9.99804677700000033e-01;
    NV_Ith_S(y, 30) =  9.99973831200000052e-01;
    NV_Ith_S(y, 31) =  9.99999990900000024e-01;
    NV_Ith_S(y, 32) =  9.99999990900000024e-01;
    NV_Ith_S(y, 33) =  2.74941404400000020e-03;
    NV_Ith_S(y, 34) = 0.999637;
    NV_Ith_S(y, 35) =  6.83207999999999982e-05;
    NV_Ith_S(y, 36) =  1.80144999999999990e-08;
    NV_Ith_S(y, 37) =  8.26618999999999954e-05;
    NV_Ith_S(y, 38) =  1.55510000000000007e-04;
    NV_Ith_S(y, 39) =  5.67622999999999969e-05;
    NV_Ith_S(y, 40) = 0.0;
    NV_Ith_S(y, 41) = 0.0;
    NV_Ith_S(y, 42) = 0.0;
    NV_Ith_S(y, 43) = 0.0;
    NV_Ith_S(y, 44) =  2.70775802499999996e-01;
    NV_Ith_S(y, 45) =  1.92850342599999990e-04;
    NV_Ith_S(y, 46) =  9.96759759399999945e-01;
    NV_Ith_S(y, 47) = 2.5e-07;
    NV_Ith_S(y, 48) = 3.12e-07;

}

/* Pacing event (non-zero stimulus) */
struct PacingEventS {
    double level;       /* The stimulus level (dimensionless, normal range [0,1]) */
    double start;       /* The time this stimulus starts */
    double duration;    /* The stimulus duration */
    double period;      /* The period with which it repeats (or 0 if it doesn't) */
    double multiplier;  /* The number of times this period occurs (or 0 if it doesn't) */
    struct PacingEventS* next;
};
typedef struct PacingEventS PacingEvent;

/*
 * Schedules a pacing event.
 * @param top The first event in a stack (the stack's head)
 * @param add The event to schedule
 * @return The new pointer to the head of the stack
 */
static PacingEvent*
PacingEvent_Schedule(PacingEvent* top, PacingEvent* add)
{
    add->next = 0;
    if (add == 0) return top;
    if (top == 0) return add;
    if (add->start <= top->start) {
        add->next = top;
        return add;
    }
    PacingEvent* evt = top;
    while(evt->next != 0 && evt->next->start <= add->start) {
        evt = evt->next;
    }
    add->next = evt->next;
    evt->next = add;
    return top;
}

/* CVODE Flags */
static int check_flag(void *flagvalue, char *funcname, int opt)
{
    int *errflag;
    /* Check if SUNDIALS function returned NULL pointer - no memory allocated */
    if (opt == 0 && flagvalue == NULL) {
        fprintf(stderr, "\nSUNDIALS_ERROR: %s() failed - returned NULL pointer\n\n", funcname);
        return(1);
    } /* Check if flag < 0 */
    else if (opt == 1) {
        errflag = (int *) flagvalue;
        if (*errflag < 0) {
            fprintf(stderr, "\nSUNDIALS_ERROR: %s() failed with flag = %d\n\n", funcname, *errflag);
            return(1);
        }
    } /* Check if function returned NULL pointer - no memory allocated */
    else if (opt == 2 && flagvalue == NULL) {
        fprintf(stderr, "\nMEMORY_ERROR: %s() failed - returned NULL pointer\n\n", funcname);
        return(1);
    }
    return 0;
}

/* Show output */
static void PrintOutput(realtype t, realtype y)
{
    #if defined(SUNDIALS_EXTENDED_PRECISION)
        printf("%4.1f     %14.6Le\n", t, y);
    #elif defined(SUNDIALS_DOUBLE_PRECISION)
        printf("%4.1f     %14.6le\n", t, y);
    #else
        printf("%4.1f     %14.6e\n", t, y);
    #endif
    return;
}

/* Run a simulation */

__declspec(dllexport) int simulate_cipa(
    double* state_inout,     /* 49 state variables, input & output */
    double cl_ms,            /* cycle length, e.g. 2000.0 */
    double ko,               /* extracellular K+, e.g. 5.4 */
    double g_kr,             /* IKr scale factor */
    double p_ca,             /* ICaL scale factor */
    double g_na,             /* INa_peak scale factor */
    double g_nal,            /* INaL scale factor */
    double g_ks,             /* IKs scale factor */
    double g_k1,             /* IK1 scale factor */
    double g_to,             /* Ito scale factor */
    int n_beats,             /* number of beats to pace */
    double dt_log,           /* logging interval, e.g. 0.1 ms */
    int n_steps,             /* number of steps = cl_ms / dt_log */
    double* out_t,           /* logged time buffer [n_steps] */
    double* out_v,           /* logged voltage buffer [n_steps] */
    double* out_inet         /* logged net current buffer [n_steps] */
) {
    int flag;
    SUNContext sundials_context;
    flag = SUNContext_Create((SUNComm)0, &sundials_context);
    if (flag != 0) return -1;

    N_Vector y = N_VNew_Serial(N_STATE, sundials_context);
    N_Vector dy = N_VNew_Serial(N_STATE, sundials_context);
    if (!y || !dy) return -2;

    /* Initialize baseline constants */
    updateConstants();

    /* Apply user/drug scales */
    AC_ko = ko;
    AC_GKr = AC_GKr * g_kr;
    AC_PCa = AC_PCa * p_ca;
    AC_PCaK = 0.0003574 * AC_PCa;
    AC_PCaNa = 0.00125 * AC_PCa;
    AC_PCap = 1.1 * AC_PCa;
    AC_PCaKp = 0.0003574 * AC_PCap;
    AC_PCaNap = 0.00125 * AC_PCap;

    AC_GNa = AC_GNa * g_na;
    AC_GNaL = AC_GNaL * g_nal;
    AC_GKs = AC_GKs * g_ks;
    AC_GK1 = AC_GK1 * g_k1;
    AC_Gto = AC_Gto * g_to;

    AC_i_Stim_Start = 50.0;
    AC_i_Stim_End = 1e17;
    AC_i_Stim_Period = cl_ms;
    AC_i_Stim_PulseDuration = 0.5;
    AC_i_Stim_Amplitude = -80.0;

    /* Copy initial state or use defaults */
    if (state_inout != NULL && state_inout[0] != 0.0) {
        for (int i = 0; i < N_STATE; i++) {
            NV_Ith_S(y, i) = state_inout[i];
        }
    } else {
        default_initial_values(y);
    }
    NV_Ith_S(y, 43) = 1.0; /* Dynamic hERG disabled invariant */

    /* Create CVODE solver */
    void* cvode_mem = CVodeCreate(CV_BDF, sundials_context);
    if (!cvode_mem) return -3;

    flag = CVodeInit(cvode_mem, rhs, 0.0, y);
    if (flag != 0) return -4;

    SUNMatrix A = SUNDenseMatrix(N_STATE, N_STATE, sundials_context);
    SUNLinearSolver LS = SUNLinSol_Dense(y, A, sundials_context);
    flag = CVodeSetLinearSolver(cvode_mem, LS, A);
    if (flag != 0) return -5;

    flag = CVodeSStolerances(cvode_mem, 1e-6, 1e-8);
    if (flag != 0) return -6;

    CVodeSetMaxNumSteps(cvode_mem, 100000);
    CVodeSetMaxStep(cvode_mem, 0.5);

    double t = 0.0;

    /* Run pacing beats */
    for (int b = 0; b < n_beats; b++) {
        t = 0.0;
        flag = CVodeReInit(cvode_mem, 0.0, y);
        if (flag != 0) return -7;

        if (b < n_beats - 1) {
            /* Discarded prepacing beat */
            flag = CVode(cvode_mem, 50.0, y, &t, CV_NORMAL);
            flag = CVode(cvode_mem, 50.5, y, &t, CV_NORMAL);
            flag = CVode(cvode_mem, cl_ms, y, &t, CV_NORMAL);
        } else {
            /* Final analysis beat */
            for (int k = 0; k < n_steps; k++) {
                double t_target = k * dt_log;
                if (t_target > 0.0) {
                    flag = CVode(cvode_mem, t_target, y, &t, CV_NORMAL);
                }
                rhs(t_target, y, dy, NULL);
                if (out_t) out_t[k] = t_target;
                if (out_v) out_v[k] = NV_Ith_S(y, 0);
                if (out_inet) {
                    out_inet[k] = AV_INaL_INaL + AV_ICaL_ICaL + AV_IKr_IKr + AV_IKs_IKs + AV_IK1_IK1 + AV_Ito_Ito;
                }
            }
        }
    }

    /* Save back final state */
    if (state_inout != NULL) {
        for (int i = 0; i < N_STATE; i++) {
            state_inout[i] = NV_Ith_S(y, i);
        }
    }

    /* Cleanup */
    CVodeFree(&cvode_mem);
    SUNLinSolFree(LS);
    SUNMatDestroy(A);
    N_VDestroy_Serial(y);
    N_VDestroy_Serial(dy);
    SUNContext_Free(&sundials_context);

    return 0;
}
