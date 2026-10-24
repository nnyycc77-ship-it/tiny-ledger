# Standing watch: change report

Watchlist: watchlist.json
Previous snapshot (UTC): 2026-10-22T21:34:25Z
This run (UTC): 2026-10-24T14:33:17Z

Entries checked: 1. Changed: 1. New: 0. No change: 0. No longer on the watchlist: 0.

## Change alerts

### GARDA CL CENTRAL INC (carrier, USDOT 2046)

- safer.Physical Address:: changed from 2000 NW CORPORATE BLVD BOCA RATON, FL   33431-7304 to 2000 NW CORPORATE BLVD BOCA RATON, FL   33431-7304
- li.record_lines: changed from US DOT: 2046, Docket Number: MC00065419, Legal Name: GARDA CL CENTRAL, INC to Docket Number:, Legal Name:

Source evidence for the new state:

### Census record (FMCSA Company Census File, DOT open data dataset az4n-8mr2)

QUERY: dot_number = 2046 returned 1 record (retrieved 2026-10-24T14:33:17Z).

- dot_number as shown: 2046
- legal_name as shown: GARDA CL CENTRAL INC
- dba_name: not present in the record
- phy_city as shown: BOCA RATON
- phy_state as shown: FL
- power_units as shown: 137
- total_drivers as shown: 84
- docket1prefix as shown: MC
- docket1 as shown: 65419
- docket1_status_code as shown: A
- safety_rating as shown: S
- safety_rating_date as shown: 20220817
- mcs150_mileage as shown: 1420000
- mcs150_mileage_year as shown: 2026
- mcs150_date as shown: 20260601
- business_org_desc as shown: CORPORATION
- carship as shown: C
- carrier_operation as shown: A
- status_code as shown: A
- classdef as shown: AUTHORIZED FOR HIRE

Source. FMCSA Company Census File record, USDOT 2046
- Query URL: https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=2046&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef
- Retrieved (UTC): 2026-10-24T14:33:17Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Server: nginx
Date: Sat, 24 Oct 2026 14:33:19 GMT
Content-Type: application/json;charset=utf-8
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Socrata-RequestId: 2cf2fc886e369be5d264d62090b6b52d
Access-Control-Allow-Origin: *
ETag: W/"aW5kaWEuMzM1NTNfNF8xMDQyN2FPTUhjeFc5YVVCYWsyZWxQVDZTZ1QzN2tZ---gzipU2vSq4r72iL54Lr2HlcdSnuoSj0--gzip--gzip"
X-SODA2-Fields: ["dot_number","legal_name","dba_name","phy_city","phy_state","power_units","total_drivers","docket1prefix","docket1","docket1_status_code","safety_rating","safety_rating_date","mcs150_mileage","mcs150_mileage_year","mcs150_date","business_org_desc","carship","carrier_operation","status_code","classdef"]
X-SODA2-Types: ["number","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text"]
X-SODA2-Data-Out-Of-Date: false
X-SODA2-Truth-Last-Modified: Sat, 24 Oct 2026 10:24:21 GMT
X-SODA2-Secondary-Last-Modified: Sat, 24 Oct 2026 10:24:21 GMT
Last-Modified: Sat, 24 Oct 2026 10:24:21 GMT
Vary: Accept-Encoding
X-Socrata-Region: aws-us-east-1-fedramp-prod
Connection: close
Transfer-Encoding: chunked

[{"dot_number":"2046","legal_name":"GARDA CL CENTRAL INC","phy_city":"BOCA RATON","phy_state":"FL","power_units":"137","total_drivers":"84","docket1prefix":"MC","docket1":"65419","docket1_status_code":"A","safety_rating":"S","safety_rating_date":"20220817","mcs150_mileage":"1420000","mcs150_mileage_year":"2026","mcs150_date":"20260601","business_org_desc":"CORPORATION","carship":"C","carrier_operation":"A","status_code":"A","classdef":"AUTHORIZED FOR HIRE"}]

```

### SAFER Company Snapshot

QUERY: query_param = USDOT, query_string = 2046 (retrieved 2026-10-24T14:33:18Z). 18 of 19 labelled fields were found in the page text. Each value below is the text that follows its label in the page; the inspection, out of service and crash tables are not parsed and are read from the complete page beneath the source link.

- Entity Type: CARRIER
- USDOT Status: ACTIVE
- Out of Service Date: None
- USDOT Number: 2046
- MCS-150 Form Date: 06/01/2026
- MCS-150 Mileage (Year): 1,420,000 (2026)
- Operating Authority Status: AUTHORIZED FOR: Motor Carrier of Property (Except Household Goods)
- MC/MX/FF Number(s): MC-65419
- Legal Name: GARDA CL CENTRAL INC
- DBA Name: none shown (blank in the source)
- Physical Address: 2000 NW CORPORATE BLVD BOCA RATON, FL   33431-7304
- Phone: (561) 939-7000
- Power Units: 68
- Non-CMV Units: 69
- Drivers: 84
- Total Inspections: label not found in the response text
- Rating Date: 08/17/2022
- Review Date: 08/10/2022
- Rating: Satisfactory

Source. FMCSA SAFER Company Snapshot, USDOT 2046
- Query URL: https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=2046
- Retrieved (UTC): 2026-10-24T14:33:18Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Sat, 24 Oct 2026 14:33:20 GMT
Content-Type: text/html
referrer-policy: strict-origin
content-security-policy: frame-ancestors 'self';
set-cookie: AWSALB=PksSMCqFfMwPjqV4Sngrl0tiDrDBKpSV+IztzqHtx2xO7wyzEdYu5EPjCFcn3DsEhJke/5dDnPT8CvWKAt0HKUDoSqdF03acSep2GQiXddmj0IHOIcwgcC3aK/9I; Expires=Sat, 31 Oct 2026 14:33:20 GMT; Path=/
set-cookie: AWSALBCORS=PksSMCqFfMwPjqV4Sngrl0tiDrDBKpSV+IztzqHtx2xO7wyzEdYu5EPjCFcn3DsEhJke/5dDnPT8CvWKAt0HKUDoSqdF03acSep2GQiXddmj0IHOIcwgcC3aK/9I; Expires=Sat, 31 Oct 2026 14:33:20 GMT; Path=/; SameSite=None; Secure
set-cookie: ASPSESSIONIDCWBBCRTQ=AHDAOKFCGOANMGKJHENGCKDO; secure; path=/
cache-control: private
server: Microsoft-IIS/10.0
x-powered-by: ASP.NET
x-frame-options: SAMEORIGIN
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-xss-protection: 1; mode=block
x-content-type-options: nosniff
Connection: close
Content-Length: 46013


<noscript>
This page requires scripting to be enabled.
</noscript>
<noscript>
This page requires scripting to be enabled.
</noscript>

<HTML>
 <HEAD>
  <TITLE>SAFER Web - Company Snapshot GARDA CL CENTRAL INC</TITLE>
  <LINK rel="stylesheet" href="safer.css" type="text/css">
  <!-- do not change the name of this page to .aspx
     some of the code will not run. If you DO change 
     it, you will need to adjust the code to work with 
     asp.net engine
 -->
<SCRIPT LANGUAGE="JavaScript">
<!-- Hide from non-javascript browsers

function format_input()
{

return;
}

function ShowPlate(FileName)
{
   if ( FileName == document.location.href )
     document.write('<IMG src="Images/bullet_hp_full.gif" width="20" height="20" border="0">');
   else
     document.write('<IMG src="Images/bullet_hp_mt.gif" width="20" height="20" border="0">'); 
}

function InitQueryBox()
{
  document.QueryBox.query_type.selectedIndex = 0;
  SetQueryParam(document.QueryBox.query_type);
  document.QueryBox.query_string.value="";
}

function SetQueryParam(ObjQueryType)
{
   var i = j = 0;
   var src;
   var srcName = "";

   queryCarrierSnapshot = new Array("USDOT Number", "USDOT", "MC/MX Number", "MC_MX","Name", "NAME");
   queryCarrierProfile  = new Array("USDOT Number", "USDOT");
   FMCSARegistration    = new Array("USDOT Number", "USDOT");
   querySafeStat        = new Array("USDOT Number", "USDOT", "Name", "NAME");
   queryLicensing       = new Array("USDOT Number", "USDOT", "MC Docket #", "MC", "MX Docket #", "MX", "FF Docket #", "FF", "Name", "NAME");

   for (i = 0; i < ObjQueryType.length; i++)
      if (ObjQueryType.options[i].selected)
         srcName = ObjQueryType.options[i].value;

   src = eval(srcName);

   with (document.QueryBox.query_param) 
   {
      options.length = 0;
      for (i = 0; i < src.length; i++)
      {

         j = options.length;
         options[j] = new Option(src[i]);
         options[j].value = src[i+1];
         i++;
      }
      options[0].selected = true;
   }
   
   if (srcName == "FMCSARegistration")
     window.location.href = "http://www.usdotnumberregistration.com";
   if (srcName == "queryCarrierProfile")
     window.location.href = "CSP_Order.asp";
   if (srcName == "Enforcement")
     window.location.href = "Enforcement";
}

function MM_jumpMenu(targ,selObj,restore){ //v3.0
  eval(targ+".location='"+selObj.options[selObj.selectedIndex].value+"'");
  if (restore) selObj.selectedIndex=0;
}


function MM_preloadImages() { //v3.0
  var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
    var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
    if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}

function MM_swapImgRestore() { //v3.0
  var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}

function MM_findObj(n, d) { //v4.0
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && document.getElementById) x=document.getElementById(n); return x;
}

function MM_swapImage() { //v3.0
  var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
   if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}


-->
</SCRIPT>
<NOSCRIPT>This Pages requires Javascript</NOSCRIPT>

  <SCRIPT language="JavaScript">
      function OpenHelp(topic)
      {
          helplink = "saferhelp.aspx#" + topic;
          window.open(helplink, '', 'scrollbars,width=200,height=150,');
      }
  </SCRIPT>
 </HEAD>
<BODY>
 <P>&nbsp;
   <!-- WRAP THE WHOLE PAGE IN A CENTERED TABLE -->
   <TABLE border="0" cellpadding="0" cellspacing="0" WIDTH="100%" ALIGN=CENTER summary="Table used for formatting purposes only">
     <TR>
       <TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
     </TR>
     <TR>
       <TH SCOPE="ROW"><div class="hidden">SAFER Table Layout</div></TH>
       <TD>
         <TABLE border="0" cellpadding="0" cellspacing="0" WIDTH="100%" summary="For formatting purpose>
           <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
           <TR>
           <TR><TD ALIGN=CENTER>
               <TABLE BORDER=0 summary="Table used for formatting purposes only">
                 <TR>
                   <TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD align=left valign=top>
                     <FORM name="QueryBox" ACTION="query.asp" METHOD="Post">

<!-- OnSubmit="format_input()" -->
<INPUT type="hidden" name="searchtype" value="ANY">
<INPUT type="hidden" name="query_type" value="queryCarrierSnapshot">
<P ALIGN=CENTER>
<TABLE cellSpacing=0 cellPadding=4 width=300 border=0 bgcolor=#c0e0ff summary="query result">
  <TR><TH SCOPE="COL"><div class="hidden">Query Result</div></TH>
  </TR>
  <TR>
    <!--following is for debugging code that keeps the user's last 
        query parameter and string stored in the session so that 
        from page to page the query form defaults to the user's
        last query.-->
    <!--td>LAST QUERY PARAM:USDOT </TD-->
    <!--td>LAST QUERY STRING:2046 </TD-->
    <TH SCOPE="ROW"><div class="hidden">Information</div></TH>
    <TD NOWRAP="nowrap"><input id="1" type="radio" name="query_param" value="USDOT"
    checked>
    <LABEL for="1">USDOT Number</LABEL></TD>
    <TD NOWRAP="nowrap"><input id="2" type="radio" name="query_param" value="MC_MX"
    >
    <LABEL for="2">MC/MX Number</LABEL></TD>
    <TD NOWRAP="nowrap"><input id="3" type="radio" name="query_param" value="NAME"
    >
    <LABEL for="3">Name</LABEL>
    </TD>
  </TR>
  <TR>
    <TH SCOPE="ROW"><div class="hidden">SAFER Table Layout</div></TH>
    <TD COLSPAN="3" ALIGN="CENTER"><LABEL for="4">Enter Value:</LABEL>&nbsp;<input id="4"type=" text" name="query_string" value="2046">
    </TD>
  </TR>
  <TR>
    <TH SCOPE="ROW"><div class="hidden">SAFER Table Layout</div></TH>
    <TD COLSPAN="3" ALIGN="CENTER"><INPUT TYPE=SUBMIT VALUE="Search">
    </TD>
  </TR>
</TABLE>
</P>
</FORM>
                   </TD>
                   <TD>
                     <P align="right">
                        <FONT size="5" face="arial" color="#2040a0">
                          <B><I>Company Snapshot</I></B><br>
                        </FONT>
                        <IMG src="Images/SAFER_hr_half.jpg" alt="horizonatal line" width=100% height=2><br>
                        <IMG src="Images/spacer.gif" alt="" width=50% height=2><br>
                        <FONT size="3" face="arial">
                          <B>GARDA CL CENTRAL INC</B><br>
                          USDOT Number: 2046<br>
                        </FONT>
                     </P>
                   </TD></TR>
                 <TR>
                   <TD COLSPAN=2>
                     <TABLE align=right BORDERCOLOR="SILVER" width=20% border=1 bgcolor=#c0e0ff cellpadding=2 cellspacing=0 summary="Other Information Options">
                       <TR>
                         <TH SCOPE="COL"><div class="hidden">Other Information Options for this carrier</div></TH>
                       </TR>
                       <TR><TD><TABLE border=0 cellpadding=2 cellspacing=2 summary="Table used for formatting purposes only">
                             <TR><TH SCOPE="COL"><div class="hidden">Carrier Information</div></TH>
                             </TR>
                             <TR><TD colspan=2 align="center">
                                 <FONT size="2" face="arial"><B>Other Information for this Carrier<br></B></FONT>
                                   <HR size=2 width=80% color=#0033cc>
                               </TD></TR>
                             <TR>
                               <TD align=right><IMG src="Images/bullet_hp.gif" alt="" width=50% height=10></TD>
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://ai.fmcsa.dot.gov/sms/safer_xfr.aspx?DOT=2046&Form=SAFER" onMouseover="return true">SMS Results</A></FONT></TD>
                             </TR><TR>
                               <TD align=right><IMG src="Images/bullet_hp.gif" alt="" width=50% height=10></TD>
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://motus.dot.gov/customer/2046/account">Licensing & Insurance</A></FONT>
                               <!-- <TD align=left><FONT style=font-size:80% face=arial>Licensing & Insurance (Currently Unavailable)</FONT>-->
                               </TD></TR></TABLE>
                     </TABLE>
                     <h4><FONT size="3" face="arial"><B>
                           <A name="ID">ID/Operations</A> |
                           <A href="#Inspections">Inspections/Crashes In US</A> |
                           <A href="#CaInspections">Inspections/Crashes In Canada</A> |
                           <A href="#Safety">Safety Rating</A><br>
                         </B></FONT></h4>
                     <FONT size="2" face="arial">
                       <B>Carriers:</B>  If you would like to update the following ID/Operations
                       information, please complete and submit form
                       <A href="http://motus.dot.gov">MCS-150</A>
                       <!--<A href="http://www.usdotnumberregistration.com">MCS-150</A>-->
                       which can be obtained
                       <!-- <A href="http://152.122.44.163/LIVIEW/pkg_registration.prc_option"> -->
                       <A href="http://www.fmcsa.dot.gov/forms/print/r-l-forms.htm">online</A>
                       or from your State FMCSA office.  If you would like to challenge the accuracy of your company's
                       safety data, you can do so using FMCSA's <a href="http://dataqs.fmcsa.dot.gov">DataQs</a> system.
                       <br><br>
                       <!--<B>Carrier and other users:</B> FMCSA provides the Company Safety Profile (CSP) to motor carriers and
                       the general public interested in obtaining greater detail on a
                       particular motor carrier's safety performance then what is captured in
                       the Company Snapshot.  To obtain a CSP please visit the <a href="https://ask.fmcsa.dot.gov/app/mcmiscatalog/c_chap4#csp">CSP order
                       page</a> or call (800)832-5660 or (703)280-4001 (Fee Required).
                       <br>-->
<a NAME="USDOTSTATUS"></a> <b><font COLOR="#004080">USDOT Status</font></b><br>
<ul>
  <li><b>ACTIVE</b>: The entity's US DOT number is active. </li>
  <li><b>INACTIVE</b>: Inactive per 49 CFR 390.19(b)(4); biennial update of MCS-150 data not completed. </li>
  <li><b>OUT-OF-SERVICE</b>: Carrier is under any type of out-of-service order and is not authorized to operate. </li>
</ul>

<a NAME="OOS"></a> <b><font COLOR="#004080">Operating Authority Status</font></b><br>
<ul>
  <li><b>AUTHORIZED FOR { Passenger, Property, HHG }</b>: This will list the specific operating authorities the carrier (or broker) is allowed to operate. </li>
  <li><b>NOT AUTHORIZED</b>: The entity does not have any operating authority and/or is not authorized to engage in interstate, for-hire operations.
    <div style="padding-left:8.5%"> <span>
 <span style="color:red;font-weight:bold">*Please Note:</span>
   <span style="font-weight:bold">NOT AUTHORIZED</span> <span style="text-decoration: underline;">does not apply</span> to <span style="font-weight:bold">Private</span> or <span style="font-weight:bold">Intrastate</span> operations.
 </span></div>
  </li>
  <li><b>OUT-OF-SERVICE</b>: Carrier is under any type of out-of-service order and is not authorized to operate. </li>
</ul>
<a NAME="OOSDate"></a> <b><font COLOR="#004080">Out of Service Date</font></b><br>
Indicates the date the company was ordered Out of Service. If there are multiple
Out of Service orders, the earliest date will be displayed. <br>
<br>
<p><span style="color:red;font-weight:bold;">Please note:</span>If there are multiple Out-of-Service orders, the earliest date will be displayed.</p>
			For help on the explanation of individual data fields, click on any
                       field name or for help of a general nature go to
                       <A href="saferhelp.aspx#General"><B>SAFER General Help</B></A>.<br>
                       <br>
                       <B>The information below reflects the content of the FMCSA management information systems as of <FONT color="#0000C0">
                       10/22/2026. </B><br>
                       
                          <br>
                          <B>To find out if this entity has a pending insurance cancellation, please <A href="http://motus.dot.gov/customer/2046/account">click here</A>.</B>
                          <br>
                       
                   </TD></TR>
   </TABLE>
 </P>
 <CENTER>
   <TABLE border=1 WIDTH=70% BORDERCOLOR=SILVER cellspacing=0 cellpadding=4 summary="For formatting purpose">
     <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
     </TR>
     <tr>
       <!-- BEGIN: USDOT INFORMATION -->
       <td colspan="4" class="querylabelbkg" style="text-align:center">USDOT INFORMATION</td>
</tr>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#EntityType">Entity Type:</A></TH>
       <TD colspan=3 class="queryfield" valign=top>
         CARRIER
         &nbsp;</TD>
         <!--<TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#Status">New Entrant Status:</A></TH>
                   <TD class="queryfield" valign=top>
                        (Active)
                       
                       &nbsp;</TD>-->
     </TR>

          <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#OOS">USDOT Status:</A></TH>
                           <TD class="queryfield" valign=top>
                        <!--ACTIVE-->  ACTIVE
                       &nbsp;</TD>
               <TH SCOPE="ROW" class="querylabelbkg" align=right><a class="querylabel" href="saferhelp.aspx#OOSDate">Out of Service Date:</a></TH>
       <TD width=30% class="queryfield"> None </TD>
     </TR>

          <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#USDOTID">USDOT Number:</A></TH>
       <TD class="queryfield" valign=top>2046&nbsp;</TD>
       <TH class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#StateID">State Carrier ID Number:</A></TH>
       <TD class="queryfield" valign=top>&nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Form Date:</A></TH>
       <TD class="queryfield" valign=top>06/01/2026&nbsp;</TD>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Mileage (Year):</A></TH>
       <TD valign=top><FONT style=font-size:80% face=arial color=#0000C0><B>1,420,000 (2026)&nbsp;</TD>
     </TR>



     
     <tr>
       <!-- BEGIN: OPERATING AUTHORITY INFORMATION -->
       <td colspan="4" class="querylabelbkg" style="text-align:center">OPERATING AUTHORITY INFORMATION</td>
</tr>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#OOS">Operating Authority Status:</A></TH>
       
       <TD  colspan="4"  width=30% class="queryfield">AUTHORIZED FOR: <br> Motor Carrier of Property (Except Household Goods) <br><br> <b style="color:black">For Licensing and Insurance details </b> <a  style="color:#0000c0" href="http://motus.dot.gov/customer/2046/account">click here.</a></TD>
       

     </TR>
          <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#ICCNumbers">MC/MX/FF Number(s):</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>
         
         <A href="http://motus.dot.gov/customer/2046/account"> MC-65419</A><br>
         
         &nbsp;</TD>

     </TR>

<tr>
       <!-- BEGIN: COMPANY INFORMATION -->
       <td colspan="4" class="querylabelbkg" style="text-align:center">COMPANY INFORMATION
        <!-- IST-600 add warning if reason changed = "Suspicious Activity Reported" -->
        
       </td>
</tr>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#Carrier">Legal Name:</A></TH>
       <TD class="queryfield" valign=top colspan=3>GARDA CL CENTRAL INC&nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DBAName">DBA Name:</A></TH>
       <TD class="queryfield" valign=top colspan=3>&nbsp;</TD>
     </TR>
         
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PhysicalAddress">Physical Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="physicaladdressvalue">
        2000 NW CORPORATE BLVD<br>
            BOCA RATON, FL &nbsp; 33431-7304
         &nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#Phone">Phone:</A></TH>
       <TD class="queryfield" valign=top colspan=3>
       (561) 939-7000
        &nbsp;</TD>
    </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#MailingAddress">Mailing Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="mailingaddressvalue">
        2000 NW CORPORATE BLVD<br>
          BOCA RATON, FL &nbsp; 33431-7304
         &nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DUNSNumber">DUNS Number:</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>45-734-852 &nbsp;</TD>
     </TR>
     <TR>
      <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PowerUnits">Power Units:</A></TH>
      <TD class="queryfield" valign=top>68&nbsp;</TD>
      <TD colspan=2 style="padding: 0;">
         <TABLE border=0 WIDTH=100% cellpadding=2 cellspacing=0>
          <!-- IST-599 add non-cmv total -->
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#NonCMV">Non-CMV Units:</A></TH>
          <TD class="queryfield" valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;">69&nbsp;</TD>
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#Drivers">Drivers:</A></TH>
          <TD valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><FONT style=font-size:80% face=arial color=#0000C0><B>84&nbsp;</TD>
        </TABLE>
        </TD>
     </TR>

     <TR>
       <!-- BEGIN: Operating Classification -->
       <TD colspan=4 class="querylabelbkg"><A class="querylabel" href="saferhelp.aspx#Class">Operation Classification:</A></TD>
     </TR>
     <TR>
       <TD colspan=4 align=center>
         <TABLE border=0 cellpadding=2 cellspacing=0 summary="Operation Classification">
           <TR><TH SCOPE="COL"><div class="hidden">Operation Classification</div></TH>
           </TR>
           <TR>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR>
                   <TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD class="queryfield" width=5%>X</TD>
                   <TD><FONT style=font-size:80% face=arial>Auth. For Hire</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Exempt For Hire</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Private(Property)</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Priv. Pass. (Business)</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD class="queryfield" width=5%></TD>
                   <TD><FONT style=font-size:80% face=arial>Priv. Pass.(Non-business)</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Migrant</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>U.S. Mail</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Fed. Gov't</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR>
                   <TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD class="queryfield" width=5%></TD>
                   <TD><FONT style=font-size:80% face=arial>State Gov't</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Local Gov't</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Indian Nation</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD class="queryfield"></TD>
                 </TR>
               </TABLE>
             </TD>
           </TR>
         </TABLE>
       </TD>
     </TR>
     <TR>
       <!-- BEGIN: Carrier Operations -->
       <TD colspan=4 class="querylabelbkg" valign=top><A class="querylabel" href="saferhelp.aspx#CarrierOP">Carrier Operation:</A></TD>
     </TR>
     <TR>
       <TD colspan=4 align=center>
         <TABLE border=0 cellpadding=2 cellspacing=0 summary="Carrier Operation">
           <TR><TH SCOPE="COL"><div class="hidden">Carrier Operation</div></TH>
           </TR>
           <TR>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR>
                   <TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Interstate</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR>
                   <TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Intrastate Only (HM)</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR>
                   <TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Intrastate Only (Non-HM)</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
           </TR>
         </TABLE>
       </TD>
     </TR>
     <TR>
       <!-- BEGIN: Shipper Operations -->
       
     <TR>
       <!-- BEGIN: Cargo Carried -->
       <TD colspan=4 class="querylabelbkg" valign=top><A class="querylabel" href="saferhelp.aspx#Cargo">Cargo Carried:</A></TD>
     </TR>
     <TR>
       <TD colspan=4 align=center>
         
         <TABLE border=0 cellpadding=2 cellspacing=0 summary="Cargo Carried">
           <TR><TH SCOPE="COL"><div class="hidden">Cargo Carried</div></TH>
           </TR>
           <TR>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>General Freight</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Household Goods</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Metal: sheets, coils, rolls</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Motor Vehicles</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Drive/Tow away</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Logs, Poles, Beams, Lumber</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Building Materials</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Mobile Homes</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Machinery, Large Objects</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Fresh Produce</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Liquids/Gases</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Intermodal Cont.</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Passengers</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Oilfield Equipment</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Livestock</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Grain, Feed, Hay</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Coal/Coke</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Meat</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Garbage/Refuse</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>US Mail</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Chemicals</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Commodities Dry Bulk</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Refrigerated Food</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Beverages</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Paper Products</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Utilities</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Agricultural/Farm Supplies</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Construction</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Water Well</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD class="queryfield">CURRENCY</TD>
                 </TR>
               </TABLE>
             </TD>
           </TR>
         </TABLE>
       </TD>
     </TR>
   </TABLE>
 </CENTER>
 </FONT>
 <br>
 <br>
 <CENTER><IMG src="Images/SAFER_hr.jpg" alt="horizontal line" width=90% height=2></CENTER>
 <br>
 <br>
 <H4><FONT size="3" face="arial"><B>
       <A href="#ID">ID/Operations</A> |
       <A name="Inspections">Inspections/Crashes In US</A> |
       <A href="#CAInspections">Inspections/Crashes In Canada</A> |
       <A href="#Safety">Safety Rating</A><br>
     </B></FONT></H4>
 <FONT size="2" face="arial">
   <B>US Inspection results for 24 months prior to: <FONT color="#0000C0">
     10/22/2026</FONT></B><br>
     <br>
     Total Inspections: <FONT color="#0000C0">4</FONT><br>
     Total IEP Inspections: <FONT color="#0000C0">0</FONT><br>
     <B>Note:</B> Total inspections may be less than the sum of vehicle, driver, and
     hazmat inspections. Go to <A href="saferhelp.aspx#Inspections">Inspections Help</A> for further
     information.<br>
 </FONT>
 <br>
 <!--  BEGIN: Inspection Data -->
 <A class="querylabel" href="saferhelp.aspx#Inspections">Inspections:</A>
 <CENTER>
   <TABLE width=70% border=1 bordercolor="silver" cellspacing=0 cellpadding=3 summary="Inspections">
     <TR>
       <TH SCOPE="COL" align="right"  width=20% class="querylabelbkg">Inspection Type</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Vehicle</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Driver</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Hazmat</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">IEP</TH>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Inspections</TH>
       <TD align="center" class="queryfield">3</TD>
       <TD align="center" class="queryfield">4</TD>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service</TH>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service %</TH>
       <TD align="center" class="queryfield">
         0%
       </TD>
       <TD align="center" class="queryfield">
         0%
       </TD>
       <TD align="center" class="queryfield">
         %
       </TD>
       <TD align="center" class="queryfield">
         0%
       </TD>
     </TR>
     
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Nat'l Average %<br><span style="color: Red">as of DATE 09/25/2026*</span></TH>
       <TD align="center"><FONT style=font-size:80% face=arial>22.26%</FONT></TD>
       <TD align="center"><FONT style=font-size:80% face=arial>6.67%</FONT></TD>
       <TD align="center"><FONT style=font-size:80% face=arial>4.44%</FONT></TD>
       <TD align="center"><FONT style=font-size:80% face=arial>N/A</FONT></TD>
     </TR>
     
   </TABLE>
   <p style="color: Red; font-weight: bold; font-size: 80%; text-align: center">*OOS rates calculated based on the most recent 24 months of inspection data per the latest monthly SAFER Snapshot.</p>
 </CENTER>
 <br>
   <TABLE width=50% align="center">
    <TR><TD><FONT size="2" face="arial" align="left"><B>Inspections</B></TD></TR>
    <TR><TD><FONT size="2" face="arial" align="left"><i>Number of roadside inspections conducted within the past two years. (Note: These inspections are distinct from the periodic inspections required under 49 CFR Part 396.17, and may not include inspection of all parts and accessories set forth in 49 CFR Part 396 Appendix A.)</i></TD></TR>
    <TR><TD><FONT size="2" face="arial" align="left"><i>The inspections listed on SAFER are conducted in accordance with the North American Standard Inspection Program which was created by the Commercial Vehicle Safety Alliance (CVSA) as the roadside inspection process for inspecting commercial motor vehicles and drivers throughout North America.</i></TD></TR>
    <TR><TD><FONT size="2" face="arial" align="left"><i>Inspections are listed as total, driver, vehicle, and Hazmat. Please see <a href="https://www.fmcsa.dot.gov/safety/question-1-can-violation-free-cvsa-level-i-or-level-v-inspection-be-used-satisfy-periodic">https://www.fmcsa.dot.gov/safety/question-1-can-violation-free-cvsa-level-i-or-level-v-inspection-be-used-satisfy-periodic</a> for more details.</i></TD></TR>
  </TABLE>
 <br>
 <br>
 <!--  BEGIN: Crash Data -->
 <FONT size="2" face="arial">
   <B>Crashes reported to FMCSA by states for 24 months prior to:
   <FONT color="#0000C0">10/22/2026</FONT></B><br>
   <br><B>Note:</B> Crashes listed represent a motor carrier’s involvement in reportable crashes, without any determination as to responsibility.<br>
 </FONT>
 <br>
 <A class="querylabel" href="saferhelp.aspx#Accidents">Crashes:</A>
 <CENTER>
   <TABLE width=70% border=1 bordercolor="silver" cellspacing=0 cellpadding=3 summary="Crashes">
     <TR>
       <TH SCOPE="COL" align="right"  width=20% class="querylabelbkg">Type</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Fatal</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Injury</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Tow</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Total</TH>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Crashes</TH>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">1</TD>
       <TD align="center" class="queryfield">2</TD>
       <TD align="center" class="queryfield">3</TD>
       <!--
       <TD align="center" class="queryfield"></TD>
       -->
     </TR>
   </TABLE>
 </CENTER>
 <br>
 <br>
 <CENTER><IMG src="Images/SAFER_hr.jpg" alt="horizontal line" width=90% height=2></CENTER>
 <br>
 <br>
 <H4><FONT size="3" face="arial"><B>
       <A href="#ID">ID/Operations</A> |
       <A href="#Inspections">Inspections/Crashes In US</A> |
       <A name="CAInspections">Inspections/Crashes In Canada</A> |
       <A href="#Safety">Safety Rating</A><br>
     </B></FONT></H4>
 <FONT size="2" face="arial">
   <B>Canadian Inspection results for 24 months prior to: <FONT color="#0000C0">
   10/22/2026</FONT></B><br>
   <br>
   Total inspections: <FONT color="#0000C0">0</FONT><br>
   <B>Note:</B> Total inspections may be less than the sum of vehicle and driver inspections. Go to <A href="saferhelp.aspx#InspectionsCA">Inspections Help</A> for further
   information.<br>
 </FONT>
 <br>
 <!--  BEGIN: Inspection Data -->
 <A class="querylabel" href="saferhelp.aspx#InspectionsCA">Inspections:</A>
 <CENTER>
   <TABLE width=70% border=1 bordercolor="silver" cellspacing=0 cellpadding=3 summary="Inspections">
     <TR>
       <TH SCOPE="COL" align="right"  width=20% class="querylabelbkg">Inspection Type</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Vehicle</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Driver</TH>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Inspections</TH>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service</TH>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service %</TH>
       <TD align="center" class="queryfield">
         0%
       </TD>
       <TD align="center" class="queryfield">
         0%
       </TD>
     </TR>
   </TABLE>
 </CENTER>
 <br>
 <br>
 <!--  BEGIN: Crash Data -->
 <FONT size="2" face="arial">
   <B>Crashes results for 24 months prior to:
   <FONT color="#0000C0">10/22/2026</FONT></B><br>
   <br><B>Note:</B> Crashes listed represent a motor carrier’s involvement in reportable crashes, without any determination as to responsibility.<br>
 </FONT>
 <br>
 <A class="querylabel" href="saferhelp.aspx#InspectionsCA">Crashes:</A>
 <CENTER>
   <TABLE width=70% border=1 bordercolor="silver" cellspacing=0 cellpadding=3 summary="Crashes">
     <TR>
       <TH SCOPE="COL" align="right"  width=20% class="querylabelbkg">Type</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Fatal</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Injury</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Tow</TH>
       <TH SCOPE="COL" align="center" width=20% class="querylabelbkg">Total</TH>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Crashes</TH>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
       <!--
       <TD align="center" class="queryfield"></TD>
       -->
     </TR>
   </TABLE>
 </CENTER>
 <br>
 <br>
 <CENTER><IMG src="Images/SAFER_hr.jpg" alt="horizontal line" width=80% height=2></CENTER>
 <br>
 <br>
 <H4><FONT size="3" face="arial"><B>
       <A href="#ID">ID/Operations</A> |
       <A href="#Inspections">Inspections/Crashes In US</A> |
       <A href="#CAInspections">Inspections/Crashes In Canada</A> |
       <A name="Safety">Safety Rating</A><br>
     </B></FONT></H4>
 <FONT size="2" face="arial">
   <I>The Federal safety rating does not necessarily reflect the safety of the
   carrier when operating in intrastate commerce.</I>
 </FONT><br>
 
 <br>
 <FONT size="2" face="arial">
   <A class="querylabel" href="saferhelp.aspx#SafetyRating">Carrier Safety Rating:</A><br>
   <br>
   <B>The rating below is current as of:
   <FONT color="#0000C0">10/22/2026</FONT></B><br>
   <br>
   <B>Review Information:</B><br>
 </FONT>
 <br>
 <CENTER>
   <TABLE border="1" bordercolor="silver" width=70% cellpadding=3 cellspacing=0 summary="Review Information">
     <TR>
       <TH SCOPE="COL"><div class="hidden">Review Information</div></TH>
     </TR>
     <TR>
       <TH SCOPE="ROW" width=20% class="querylabelbkg">Rating Date:</TH>
       <TD width=30% class="queryfield">08/17/2022 </TD>
       <TH SCOPE="ROW" width=20% class="querylabelbkg">Review Date:</TH>
       <TD width=30% class="queryfield">08/10/2022 </TD>
       </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg">Rating:</TH>
       <TD class="queryfield">Satisfactory </TD>
       <TH SCOPE="ROW" class="querylabelbkg">Type:</TH>
       <TD class="queryfield">Compliance Review </TD>
     </TR>
   </TABLE>
 
 <br>
 <!-- BEGIN: End of display loop -->
 
 <!-- BEGIN: End of display loop -->
 
 <br>
 </TD>
 <!-- THE ENTIRE PAGE IS WRAPPED IN A CENTERED TABLE
      HERE ARE THE END TAGS FOR THE TABLE -->
 </TD></TR><TR>
 <TD align=center style="font-size:80%">
 
                 
<table border="0" width="960" align="center" cellpadding="0" cellspacing="0" style="border: solid 0px #e8e8e8;">
  <!-- footer-->
<tr>
    <td colspan="3">
            &#160;
     </td>
</tr>
<tr>
     <td colspan="3" align="center">
          <div id="footerbox">
          <div id="nestedbox" style="background: url(images/logo_footer.gif) no-repeat scroll 20px 40% #FFFFFF;">
         </div>
	<p>
   	<a href="" class="footer_link">SAFER Home</a> <span class="footer_white_text">|</span> 
	
   <a href="http://www.fmcsa.dot.gov/feedback.htm" class="footer_link">Feedback</a>
   <span class="footer_white_text">|</span> 
   <a href="http://www.fmcsa.dot.gov/Online-Privacy-Policy.aspx" class="footer_link">Privacy Policy</a> 
   <span class="footer_white_text">|</span>
   <a href="http://www.usa.gov/" class="footer_link">USA.gov</a> 
   <span class="footer_white_text">|</span> 
   <a href="http://www.fmcsa.dot.gov/foia/foia.htm" class="footer_link">Freedom of Information Act (FOIA)</a> 
   <span class="footer_white_text">|</span> 
   <a href="http://www.fmcsa.dot.gov/508disclaimer.htm" class="footer_link">Accessibility</a> 
   <span class="footer_white_text">|</span>
   <a href="http://www.oig.dot.gov/Hotline" class="footer_link">OIG Hotline</a> 
   <span class="footer_white_text">|</span> 
   <a href="http://www.fmcsa.dot.gov/about/WebPoliciesAndImportantLinks.htm" class="footer_link">Web Policies and Important Links</a> 
   <span class="footer_white_text">|</span> 
   <a href="http://www.fmcsa.dot.gov/plugins.htm" class="footer_link">Plug-ins </a>
   <br />
</p>
<p>
    <span class="footer_title_text">Federal Motor Carrier Safety Administration</span><br />
    <span class="footer_white_text">1200 New Jersey Avenue SE, Washington, DC 20590 &#8226; 1-800-832-5660 &#8226; TTY: 1-800-877-8339 &#8226;</span>
    <a href="http://www.fmcsa.dot.gov/about/contact/offices/displayfieldroster.asp" class="footer_link">Field Office Contacts</a>
</p>
	<p style="margin-bottom: 0em;">&#160;</p>
	</div>
     </td>
</tr>
</table>

 </TD></TR>
 </TABLE>
</BODY>
</HTML>
<!-- END: Output Page Formatting -->

```

### Licensing and Insurance

QUERY: n_dotno = 2046, s_prefix = MC, pv_vpath = LIVIEW (retrieved 2026-10-24T14:33:20Z). 2 record text lines found.

- As shown: Docket Number:
- As shown: Legal Name:

Source. FMCSA Licensing and Insurance carrier search, USDOT 2046
- Query URL: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=2046&s_prefix=MC&pv_vpath=LIVIEW
- Retrieved (UTC): 2026-10-24T14:33:20Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Sat, 24 Oct 2026 14:33:21 GMT
Content-Type: text/html; charset=WINDOWS-1252
strict-transport-security: max-age=31536000
content-language: en
server: 
x-frame-options: SAMEORIGIN
content-security-policy: frame-ancestors 'self';
Connection: close
Content-Length: 17589

<html>
<head>
<title>Licensing & Insurance Carrier Search</title>
<html>
<head>
<title>FMCSA Licensing and Insurance Web Site</title>
<script type="text/javascript" src="/lihtml/entourage.js"></script>
<script type="text/javascript" src="/lihtml/googleanalytics.js"></script>
<script type="text/javascript" src="/lihtml/dot_analytics.js"></script>
<noscript>Script edits data entry fields for valid data and required field.  The application may not work correctly without these scripts.</noscript>
</head>
<SCRIPT SRC="/lihtml/calendar.js"></SCRIPT>
<NOSCRIPT>Script provides pop-up calendar.  The application may not work correctly without this script</NOSCRIPT>
<script language="JavaScript">
         <!--
           function CheckMenu(form)
           {
           for (i=0; i < form.elements.length; i++){
             if (form.elements[i].type == "select-one"){
              j = form.elements[i].selectedIndex;
               if (j == 0) {
                alert( "Please Select a Menu Option." );
                form.elements[i].focus();
                return false;
               }
               else {
               return true;
               }
              }
            }
           }
         // -->
         </script>
<NOSCRIPT>Script edits selection as a required field.  The application may not work correctly without this script</NOSCRIPT>
<link rel="stylesheet" href="/lihtml/li.css">
<body bgcolor="#ffffff"><font size=2 face="Arial, Helvetica">
<a href="#skiplink"><img src="blank.gif" alt="Skip to Main Content" width=1 height=1 border=0></a>
<table border="0" align="center" cellpadding="0" cellspacing="0">
              <tr>
                 <td style="position:relative;">
                   <div style="position:relative;">
                   <img src="/lihtml/l_i_logo_public.gif" alt="FMCSA License and Insurance logo" />
<div style="position:absolute;  top:40px; right:10px;">
<table border="0" cellspacing="0" cellpadding="0" align="right" SUMMARY="Table used for formatting purposes only">
<tr><td align=right>
<form action="/LIVIEW/pkg_menu.prc_menu" method="post" name="Dropdown" onSubmit="return CheckMenu(this)">
<font size=-15 color="white"><label for="menu">Menu</label></font><font size=3 "white" face="Arial, Helvetica"></font>
<select id="menu" name="pv_choice">
<option selected value="ZZZ">Choose Menu Option
<option value=CARR_SEARCH>Carrier Search
<option value=HOME>Home Page
</select>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="image" src="/lihtml/go.gif" align=absmiddle ALT="Menu Go">
<input type="hidden" name="pv_vpath" value="LIVIEW" />
</form>
</td>
</tr>
</table>
</div>
</div></td>
</tr></table>
<a name="skiplink"></a>
<script src="https://www.google.com/recaptcha/api.js"></script>
<script language=javascript>
  <!--
     function isEmpty(inputStr1, inputStr2, inputStr3, inputStr4, inputStr5)
     {
      //if ((inputStr1.value == "" || inputStr1.value == null) &&
      //    (inputStr2.value == "" || inputStr2.value == null) &&
      //    (inputStr3.value == "" || inputStr3.value == null) &&
      //    (inputStr4.value == "" || inputStr4.value == null) &&
      //    (inputStr5.value == "" || inputStr5.value == null || inputStr5.value=="~~"))

      if ((inputStr1.value == "") &&
          (inputStr2.value == "") &&
          (inputStr3.value == "") &&
          (inputStr4.value == "") &&
          ((inputStr5.value == "") || (inputStr5.value=="~~")))
      {
       inputStr1.focus();
       return true;
      }
      return false;
     }

     function isEmpty2(inputStr1, inputStr2, inputStr3)
     {
      //if ((inputStr1.value == "" || inputStr1.value == null) &&
      //    (inputStr2.value == "" || inputStr2.value == null) &&
      //    (inputStr3.value == "" || inputStr3.value == null || inputStr3.value=="~~"))
      if ((inputStr1.value == "") &&
         (inputStr2.value == "") &&
         ((inputStr3.value == "")||(inputStr3.value=="~~")))
      {
       inputStr3.focus();
       return true;
      }
      return false;
     }

     function isInteger(theElement)
     {
      var x = Math.floor(theElement.value)
      if (( x != theElement.value ) || ( x < 0 ))
      {
       theElement.focus();
       return true;
      }
      return false;
     }

     function isValid(n_dotno, n_docketno, s_legalname, s_dbaname, s_state) {

       document.getElementsByName("g_recaptcha_response")[0].value  = document.getElementsByName("g-recaptcha-response")[0].value;
       document.getElementsByName("g-recaptcha-response")[0].disabled = true;

       if (isEmpty(n_dotno, n_docketno, s_legalname, s_dbaname, s_state)) {
               alert("The entries are empty. Please try again.");
               return false;
       } else {
         if (isEmpty2(n_dotno, n_docketno, s_state)) {
            alert("Queries for name only will take too long. Please enter state as well to limit your query.");
            return false;
         } else {
           if (isInteger(n_dotno)) {
              alert("Sorry, Your Entry for USDOT Number Must Be a Valid Integer.");
              return false;
           } else {
             if (isInteger(n_docketno)) {
                alert("Sorry, Your Entry for Docket Number Must Be a Valid Integer.");
                return false;
             }
           }
         }
       }
       return true;
     }
  // -->
  </script>
<noscript> Script checks for verifications. The application may not work correctly without this script</noscript>
</head>
<br />
Enter information for query.
         If you know the <b><font color="#cc3300">USDOT Number</font></b> or <b><font color="#cc3300">Docket Number</font></b>,
         that is all that needs to be entered. If you do not know the <b><font color="#cc3300">USDOT Number</font></b>
         or <b><font color="#cc3300">Docket Number</font></b>, you can search on any combination of
         <b><font color="#cc3300">Legal Name, DBA Name (Doing-Business-As Name)</font></b>, or <b><font color="#cc3300">State</font></b>
         to narrow the search. If searching by name please use a state to limit the search. The search always looks for a legal or DBA name which begins with the
         text entered.  If the wild card character <b><font color="#cc3300">( * )</font></b> is the first position entered, the search will
         look for a legal or DBA name which contains the text entered, but this search will take longer.
         <br><br><center><font color="#cc3300"><B>Please enter the challenge question.</B></font>
         <form action="/LIVIEW/pkg_carrquery.prc_carrlist" method="post" name="search">
         <table SUMMARY="table used for formatting purposes only">
         <tr>
            <td align=right>
               <b><font color="#336699" face="Arial, Helvetica" size=+1><label for="usdot_number">USDOT Number:</label></font></b>
            </td>
            <td>
              <input type="text" id="usdot_number" NAME="n_dotno" value="2046" MAXLENGTH="8" size="27">
            </td>
         </tr>
         <tr>
            <td align=right>
               <b><font color="#336699" face="Arial, Helvetica" size=+1><label for="docket_number">Docket Number:</label></font></b>
            </td>
            <td>
               <select NAME="s_prefix" id="docket_number" size="1">
                  <option selected value="MC">MC
                  <option >FF
                  <option >MX
               </select>
               <input type="text" id="docket_number" NAME="n_docketno" value="" MAXLENGTH="8" size="20">
            </td>
         </tr>
         <tr>
            <td align=right>
               <b><font color="#336699" face="Arial, Helvetica" size=+1><label for="legal_name">Legal Name:</label></font></b>
            </td>
            <td>
               <input type="text" NAME="s_legalname" id="legal_name" value="" MAXLENGTH="120" size="27">
            </td>
         </tr>
         <tr>
            <td align=right>
               <b><font color="#336699" face="Arial, Helvetica" size=+1><label for="dba_name">DBA Name:</label></font></b>
            </td>
            <td>
               <input type="text" NAME="s_dbaname" id="dba_name" value="" MAXLENGTH="60" size="27">
            </td>
         </tr>
         <tr>
            <td align=right>
               <b><font color="#336699" face="Arial, Helvetica" size=+1><label for="state">State:</label></font></b>
            </td>
            <td>
<select name = "s_state" id="state">
<option value="~~">Select State/Country
<option value=ALUS>ALABAMA
<option value=AKUS>ALASKA
<option value=ASUS>AMERICAN SAMOA
<option value=AZUS>ARIZONA
<option value=ARUS>ARKANSAS
<option value=CAUS>CALIFORNIA
<option value=COUS>COLORADO
<option value=CTUS>CONNECTICUT
<option value=DEUS>DELAWARE
<option value=DCUS>DISTRICT OF COLUMBIA
<option value=FMUS>FEDERATED STATES OF MICRONESIA
<option value=FLUS>FLORIDA
<option value=GAUS>GEORGIA
<option value=GUUS>GUAM
<option value=HIUS>HAWAII
<option value=IDUS>IDAHO
<option value=ILUS>ILLINOIS
<option value=INUS>INDIANA
<option value=IAUS>IOWA
<option value=KSUS>KANSAS
<option value=KYUS>KENTUCKY
<option value=LAUS>LOUISIANA
<option value=MEUS>MAINE
<option value=MHUS>MARSHALL ISLANDS
<option value=MDUS>MARYLAND
<option value=MAUS>MASSACHUSETTS
<option value=MIUS>MICHIGAN
<option value=MNUS>MINNESOTA
<option value=MSUS>MISSISSIPPI
<option value=MOUS>MISSOURI
<option value=MTUS>MONTANA
<option value=NEUS>NEBRASKA
<option value=NVUS>NEVADA
<option value=NHUS>NEW HAMPSHIRE
<option value=NJUS>NEW JERSEY
<option value=NMUS>NEW MEXICO
<option value=NYUS>NEW YORK
<option value=NCUS>NORTH CAROLINA
<option value=NDUS>NORTH DAKOTA
<option value=MPUS>NORTHERN MARIANA ISLANDS
<option value=OHUS>OHIO
<option value=OKUS>OKLAHOMA
<option value=ORUS>OREGON
<option value=PWUS>PALAU
<option value=PAUS>PENNSYLVANIA
<option value=PRUS>PUERTO RICO
<option value=RIUS>RHODE ISLAND
<option value=SCUS>SOUTH CAROLINA
<option value=SDUS>SOUTH DAKOTA
<option value=TNUS>TENNESSEE
<option value=TXUS>TEXAS
<option value=UMUS>U.S. MINOR OUTLYING ISLANDS
<option value=XXUS>UNKNOWN STATE
<option value=AAUS>US ARMED FORCES - AMERICAS
<option value=AEUS>US ARMED FORCES - EUROPE
<option value=APUS>US ARMED FORCES - PACIFIC
<option value=UTUS>UTAH
<option value=VTUS>VERMONT
<option value=VIUS>VIRGIN ISLANDS
<option value=VAUS>VIRGINIA
<option value=WAUS>WASHINGTON
<option value=WVUS>WEST VIRGINIA
<option value=WIUS>WISCONSIN
<option value=WYUS>WYOMING
<option value=AGMX>AGUASCALIENTES, MEXICO
<option value=BAMX>BAJA CALIFORNIA, MEXICO
<option value=BCMX>BAJA CALIFORNIA SUR, MEXICO
<option value=CAMX>CAMPECHE, MEXICO
<option value=CPMX>CHIAPAS, MEXICO
<option value=CHMX>CHIHUAHUA, MEXICO
<option value=COMX>COAHUILA, MEXICO
<option value=CLMX>COLIMA, MEXICO
<option value=DFMX>DISTRITO FEDERAL, MEXICO
<option value=DUMX>DURANGO, MEXICO
<option value=GJMX>GUANAJUATO, MEXICO
<option value=GRMX>GUERRERO, MEXICO
<option value=HDMX>HIDALGO, MEXICO
<option value=JLMX>JALISCO, MEXICO
<option value=MXMX>MEXICO, MEXICO
<option value=MCMX>MICHOACAN, MEXICO
<option value=MRMX>MORELOS, MEXICO
<option value=NAMX>NAYARIT, MEXICO
<option value=NLMX>NUEVO LEON, MEXICO
<option value=OAMX>OAXACA, MEXICO
<option value=PUMX>PUEBLA, MEXICO
<option value=QUMX>QUERETARO, MEXICO
<option value=QRMX>QUINTANA ROO, MEXICO
<option value=SLMX>SAN LUIS POTOSI, MEXICO
<option value=SIMX>SINALOA, MEXICO
<option value=SOMX>SONORA, MEXICO
<option value=TAMX>TABASCO, MEXICO
<option value=TMMX>TAMAULIPAS, MEXICO
<option value=TLMX>TLAXCALA, MEXICO
<option value=VEMX>VERACRUZ, MEXICO
<option value=YUMX>YUCATAN, MEXICO
<option value=ZAMX>ZACATECAS, MEXICO
<option value=ABCA>ALBERTA, CANADA
<option value=BCCA>BRITISH COLUMBIA, CANADA
<option value=CACA>CANADA, CANADA
<option value=MBCA>MANITOBA, CANADA
<option value=NBCA>NEW BRUNSWICK, CANADA
<option value=NLCA>NEWFOUNDLAND, CANADA
<option value=NTCA>NORTHWEST TERRITORIES, CANADA
<option value=NSCA>NOVA SCOTIA, CANADA
<option value=NUCA>NUNAVUT, CANADA
<option value=ONCA>ONTARIO, CANADA
<option value=PECA>PRINCE EDWARD ISLAND, CANADA
<option value=QCCA>PROVINCE OF QUEBEC, CANADA
<option value=SKCA>SASKATCHEWAN, CANADA
<option value=YTCA>YUKON TERRITORY, CANADA
</select>
</td></tr>
<tr>
<table align="center" width="80%" class="table_without_border" SUMMARY="">
<tr>
<td colspan="2" align="center"><div class="g-recaptcha" data-sitekey="6Ldbx1gUAAAAAMEylxZ_DoZS430WhNsmV47Y5t58"></div></td>
<input type="hidden" name="g_recaptcha_response" value="">
</tr>
</table>
</tr>
<tr><table><tr>
            <td align=center colspan="2"><font size="2" color="blue">New applications will not be reflected in search results for 24 hours after filing</font></td>
            </tr></table></tr>
<tr>
         <td align=center colspan="2">
         <input type="submit"  value="   Search   " OnClick="return isValid(n_dotno, n_docketno, s_legalname, s_dbaname, s_state);">
<input type="reset"   value="   Reset    ">
<input type="hidden" name="pv_vpath" value="LIVIEW">
         </td>
         <td></td>
         </tr>
         </table>
         </form>
</center>
<script language="JavaScript">
      <!--
      function another_window(h_name)
      {
      window.open(h_name);
      return;
      }
      // -->
      </script>
<NOSCRIPT>Displays another window.  The application may not work correctly without this script</NOSCRIPT>
</center>
<br />
<SPAN class="footer_title_text" align="left"> October 24, 2026</SPAN>
<center>
<style type="text/css">

    a.footer_link:link, a.footer_link:visited, a.footer_link:hover, a.footer_link:active
    {
    font-size: 10px; font-family: Arial;
    color: rgb(102,102,102);
    font-weight: normal;
    text-decoration: none;
    }

    a.footer_link:visited
    {
    font-size: 10px;
    font-family: Arial;
    }

    a.footer_link:hover
    {
    font-size: 10px;
    color: #012255;
    text-decoration: underline;
    font-family: Arial;
    }

    SPAN.footer_white_text, SPAN.footer_title_text
    {
    font-size: 10px; font-family: Arial;
    color: rgb(102,102,102);
    font-weight: normal;
    text-decoration: none;
    }
    hr
    {
    border: 1;
    height:1px;
    color:cccccc;
    }
    .vertical-line
    {
    width: 1px;
    height: 60;
    }
    .vcontrol
    {
    font-size: 4px;
    font-family: Arial;
    height:8;
    }
  </style>
<HR width="98%" height="12"></HR>
<TABLE align= "left" border ="0" cellpadding="0" cellspacing="0">
<TBODY>
<tr>
<TD>
<img id="NetFYIBigImg" src="/lihtml/logo_footer.gif" Alt="USDOT logo" />
</TD>
<TD align="center" width="1">
<td align="center" width="1" bgcolor="#cccccc"><BR></td>
<TD align="middle" colSpan="2">
<td>
<TABLE align= "center" border ="0" cellpadding="0" cellspacing="0">
<tr>
<td align="center">
<A class="footer_link" href="https://www.fmcsa.dot.gov/" TARGET="_blank" title="FMCSA Home">FMCSA Home</A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.dot.gov/" TARGET="_blank" title="DOT Home">DOT Home</A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/feedback.htm" TARGET="_blank" title="Go to Feedback">Feedback</A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/Online-Privacy-Policy.aspx" TARGET="_blank" title="Go to Privacy Policy">Privacy Policy </A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/redirect.aspx?page=https://www.usa.gov/" TARGET="_blank" title="Go to USA gov">USA.gov</A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/foia/foia.htm" TARGET="_blank" title="Go to Freedom of Information Act">Freedom of Information Act (FOIA)</A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/508disclaimer.htm" TARGET="_blank" title="Go to Accessibility">Accessibility</A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/redirect.aspx?page=https://www.oig.dot.gov/Hotline" TARGET="_blank" title="Go to OIG Hotline"> OIG Hotline </A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/about/WebPoliciesAndImportantLinks.htm" TARGET="_blank" title="Go to Web Policies and Important Links"> Web Policies and Important Links </A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/plugins.htm" TARGET="_blank" title="Get Plug Ins">Plug-ins </A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="/LIVIEW/pkg_li_std_routines.prc_related_sites?pv_vpath=LIVIEW" TARGET="_blank" title="Related Sites">Related Sites</A>
<SPAN class="footer_white_text">|</SPAN>
<A class="footer_link" href="/LIVIEW/pkg_li_std_routines.prc_help?pn_pageid=5" TARGET="_blank" title="FMCSA Home">Help</A>
</td>
</tr>
<tr class="vcontrol"><td>&nbsp;</td>
</tr>
<tr>
<td align="center">
<SPAN class="footer_title_text"> Federal Motor Carrier Safety Administration </SPAN>
<BR />
<SPAN class="footer_white_text">1200 New Jersey Avenue SE, Washington, DC 20590 - 1-800-832-5660 - TTY: 1-800-877-8339 - </SPAN>
<A class="footer_link" href="https://www.fmcsa.dot.gov/about/contact/offices/displayfieldroster.asp" TARGET="_blank" title="Go to Field Office Contacts">  Field Office Contacts </A>
</TD>
</tr>
<tr>
<TD colSpan="3" height="20"></TD>
<TD colSpan="3" height="20"></TD>
<TD colSpan="3" height="20"></TD>
</tr>
</table>
</td>
</TR>
</TBODY>
</table>
</center>
</body>
</html>
</body>
</html>

```
