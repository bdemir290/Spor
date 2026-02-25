@echo off
chcp 65001 >nul
REM Asagidaki yolu kendi proje klasorunuzle degistirin. Masaustune kopyalayinca bu yol gerekli.
cd /d "%~dp0"
REM Alternatif: Sabit yol kullanmak icin ust satiri kapatip alttaki satiri acin:
REM cd /d "C:\Users\Berke.Demir\Desktop\Pakistan\mANİFEST\Yeni klasör\spor_uygulamasi"
echo Spor ve Beslenme Takip uygulamasi baslatiliyor...
echo Tarayicida acilacak: http://localhost:8501
echo Telefondan baglanmak icin terminalde "Network URL" adresini kullanin.
echo.
python -m streamlit run app.py
pause
