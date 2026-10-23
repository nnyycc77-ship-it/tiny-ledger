# Standing watch: baseline edition

Watchlist: watchlist.json
Run (UTC): 2026-10-23T21:57:11Z

The first run on a list establishes the baseline: the state of every entry as the public record shows it now. Later runs pull the same sources again and report only what changed against this baseline. Every value below is as shown in its source; the complete raw response for each query is printed beneath its source link, and the same pulls are stored in this run's snapshot file with their SHA-256 hashes.

## OLD DOMINION FREIGHT LINE INC (carrier, USDOT 90849)

### Fields that matter

| Field | Value as shown |
| --- | --- |
| census.record_count | 1 |
| census.dot_number | 90849 |
| census.legal_name | OLD DOMINION FREIGHT LINE INC |
| census.dba_name | not present in the record |
| census.phy_city | THOMASVILLE |
| census.phy_state | NC |
| census.power_units | 10313 |
| census.total_drivers | 10341 |
| census.docket1prefix | MC |
| census.docket1 | 107478 |
| census.docket1_status_code | A |
| census.safety_rating | S |
| census.safety_rating_date | 19950929 |
| census.mcs150_mileage | 755515218 |
| census.mcs150_mileage_year | 2025 |
| census.mcs150_date | 20260915 |
| census.business_org_desc | CORPORATION |
| census.carship | C;S;B |
| census.carrier_operation | A |
| census.status_code | A |
| census.classdef | AUTHORIZED FOR HIRE |
| safer.Entity Type: | CARRIER/SHIPPER/BROKER |
| safer.USDOT Status: | ACTIVE |
| safer.Out of Service Date: | None |
| safer.USDOT Number: | 90849 |
| safer.MCS-150 Form Date: | 09/15/2026 |
| safer.MCS-150 Mileage (Year): | 755,515,218 (2025) |
| safer.Operating Authority Status: | AUTHORIZED FOR: Motor Carrier of Property (Except Household Goods) Broker of Property (Except Household Goods) |
| safer.MC/MX/FF Number(s): | MC-107478 |
| safer.Legal Name: | OLD DOMINION FREIGHT LINE INC |
| safer.DBA Name: | none shown (blank in the source) |
| safer.Physical Address: | 500 OLD DOMINION WAY THOMASVILLE, NC   27360-8923 |
| safer.Phone: | (800) 235-5569 |
| safer.Power Units: | 10,313 |
| safer.Non-CMV Units: | 0 |
| safer.Drivers: | 10,341 |
| safer.Total Inspections: | label not found in the response text |
| safer.Rating Date: | 09/29/1995 |
| safer.Review Date: | 02/09/2023 |
| safer.Rating: | Satisfactory |
| li.record_lines | Docket Number:, Legal Name: |

### Source evidence

### Census record (FMCSA Company Census File, DOT open data dataset az4n-8mr2)

QUERY: dot_number = 90849 returned 1 record (retrieved 2026-10-23T21:57:11Z).

- dot_number as shown: 90849
- legal_name as shown: OLD DOMINION FREIGHT LINE INC
- dba_name: not present in the record
- phy_city as shown: THOMASVILLE
- phy_state as shown: NC
- power_units as shown: 10313
- total_drivers as shown: 10341
- docket1prefix as shown: MC
- docket1 as shown: 107478
- docket1_status_code as shown: A
- safety_rating as shown: S
- safety_rating_date as shown: 19950929
- mcs150_mileage as shown: 755515218
- mcs150_mileage_year as shown: 2025
- mcs150_date as shown: 20260915
- business_org_desc as shown: CORPORATION
- carship as shown: C;S;B
- carrier_operation as shown: A
- status_code as shown: A
- classdef as shown: AUTHORIZED FOR HIRE

Source. FMCSA Company Census File record, USDOT 90849
- Query URL: https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=90849&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef
- Retrieved (UTC): 2026-10-23T21:57:11Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Server: nginx
Date: Fri, 23 Oct 2026 21:57:14 GMT
Content-Type: application/json;charset=utf-8
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Socrata-RequestId: 832d9a5244dc12b770a735397f34c5c7
Access-Control-Allow-Origin: *
ETag: W/"aW5kaWEuMzM1NTNfNF8xMDQxeF9XWko2OWZzTVl6RXVrU0VLTTJMYVdibjBj---gzipwRp7Ck3eMv2VAQFIYb8-DKc1nzc--gzip--gzip"
X-SODA2-Fields: ["dot_number","legal_name","dba_name","phy_city","phy_state","power_units","total_drivers","docket1prefix","docket1","docket1_status_code","safety_rating","safety_rating_date","mcs150_mileage","mcs150_mileage_year","mcs150_date","business_org_desc","carship","carrier_operation","status_code","classdef"]
X-SODA2-Types: ["number","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text"]
X-SODA2-Data-Out-Of-Date: false
X-SODA2-Truth-Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
X-SODA2-Secondary-Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
Vary: Accept-Encoding
X-Socrata-Region: aws-us-east-1-fedramp-prod
Connection: close
Transfer-Encoding: chunked

[{"dot_number":"90849","legal_name":"OLD DOMINION FREIGHT LINE INC","phy_city":"THOMASVILLE","phy_state":"NC","power_units":"10313","total_drivers":"10341","docket1prefix":"MC","docket1":"107478","docket1_status_code":"A","safety_rating":"S","safety_rating_date":"19950929","mcs150_mileage":"755515218","mcs150_mileage_year":"2025","mcs150_date":"20260915","business_org_desc":"CORPORATION","carship":"C;S;B","carrier_operation":"A","status_code":"A","classdef":"AUTHORIZED FOR HIRE"}]

```

### SAFER Company Snapshot

QUERY: query_param = USDOT, query_string = 90849 (retrieved 2026-10-23T21:57:13Z). 18 of 19 labelled fields were found in the page text. Each value below is the text that follows its label in the page; the inspection, out of service and crash tables are not parsed and are read from the complete page beneath the source link.

- Entity Type: CARRIER/SHIPPER/BROKER
- USDOT Status: ACTIVE
- Out of Service Date: None
- USDOT Number: 90849
- MCS-150 Form Date: 09/15/2026
- MCS-150 Mileage (Year): 755,515,218 (2025)
- Operating Authority Status: AUTHORIZED FOR: Motor Carrier of Property (Except Household Goods) Broker of Property (Except Household Goods)
- MC/MX/FF Number(s): MC-107478
- Legal Name: OLD DOMINION FREIGHT LINE INC
- DBA Name: none shown (blank in the source)
- Physical Address: 500 OLD DOMINION WAY THOMASVILLE, NC   27360-8923
- Phone: (800) 235-5569
- Power Units: 10,313
- Non-CMV Units: 0
- Drivers: 10,341
- Total Inspections: label not found in the response text
- Rating Date: 09/29/1995
- Review Date: 02/09/2023
- Rating: Satisfactory

Source. FMCSA SAFER Company Snapshot, USDOT 90849
- Query URL: https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=90849
- Retrieved (UTC): 2026-10-23T21:57:13Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:57:15 GMT
Content-Type: text/html
referrer-policy: strict-origin
content-security-policy: frame-ancestors 'self';
set-cookie: AWSALB=39NDEdxT5OuXXQLW2tFWijGOTdjoIbeaSdQa6ocpPPYC/awYvO4gC0y4vn4lTURe7n0rbyxOkBkDP+zlPt7BLuQzmMfxxoRiFFksV2CRSIrBRj7hvYJkcKfPbtj0; Expires=Fri, 30 Oct 2026 21:57:15 GMT; Path=/
set-cookie: AWSALBCORS=39NDEdxT5OuXXQLW2tFWijGOTdjoIbeaSdQa6ocpPPYC/awYvO4gC0y4vn4lTURe7n0rbyxOkBkDP+zlPt7BLuQzmMfxxoRiFFksV2CRSIrBRj7hvYJkcKfPbtj0; Expires=Fri, 30 Oct 2026 21:57:15 GMT; Path=/; SameSite=None; Secure
set-cookie: ASPSESSIONIDQESRRADS=GECPOILBLGPHBMMGOMOEIFGC; secure; path=/
cache-control: private
server: Microsoft-IIS/10.0
x-powered-by: ASP.NET
x-frame-options: SAMEORIGIN
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-xss-protection: 1; mode=block
x-content-type-options: nosniff
Connection: close
Content-Length: 46155


<noscript>
This page requires scripting to be enabled.
</noscript>
<noscript>
This page requires scripting to be enabled.
</noscript>

<HTML>
 <HEAD>
  <TITLE>SAFER Web - Company Snapshot OLD DOMINION FREIGHT LINE INC</TITLE>
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
    <!--td>LAST QUERY STRING:90849 </TD-->
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
    <TD COLSPAN="3" ALIGN="CENTER"><LABEL for="4">Enter Value:</LABEL>&nbsp;<input id="4"type=" text" name="query_string" value="90849">
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
                          <B>OLD DOMINION FREIGHT LINE INC</B><br>
                          USDOT Number: 90849<br>
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
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://ai.fmcsa.dot.gov/sms/safer_xfr.aspx?DOT=90849&Form=SAFER" onMouseover="return true">SMS Results</A></FONT></TD>
                             </TR><TR>
                               <TD align=right><IMG src="Images/bullet_hp.gif" alt="" width=50% height=10></TD>
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://motus.dot.gov/customer/90849/account">Licensing & Insurance</A></FONT>
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
                       10/21/2026. </B><br>
                       
                          <br>
                          <B>To find out if this entity has a pending insurance cancellation, please <A href="http://motus.dot.gov/customer/90849/account">click here</A>.</B>
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
         CARRIER/SHIPPER/BROKER
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
       <TD class="queryfield" valign=top>90849&nbsp;</TD>
       <TH class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#StateID">State Carrier ID Number:</A></TH>
       <TD class="queryfield" valign=top>&nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Form Date:</A></TH>
       <TD class="queryfield" valign=top>09/15/2026&nbsp;</TD>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Mileage (Year):</A></TH>
       <TD valign=top><FONT style=font-size:80% face=arial color=#0000C0><B>755,515,218 (2025)&nbsp;</TD>
     </TR>



     
     <tr>
       <!-- BEGIN: OPERATING AUTHORITY INFORMATION -->
       <td colspan="4" class="querylabelbkg" style="text-align:center">OPERATING AUTHORITY INFORMATION</td>
</tr>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#OOS">Operating Authority Status:</A></TH>
       
       <TD  colspan="4"  width=30% class="queryfield">AUTHORIZED FOR: <br> Motor Carrier of Property (Except Household Goods) <br>  Broker of Property (Except Household Goods) <br><br> <b style="color:black">For Licensing and Insurance details </b> <a  style="color:#0000c0" href="http://motus.dot.gov/customer/90849/account">click here.</a></TD>
       

     </TR>
          <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#ICCNumbers">MC/MX/FF Number(s):</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>
         
         <A href="http://motus.dot.gov/customer/90849/account"> MC-107478</A><br>
         
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
       <TD class="queryfield" valign=top colspan=3>OLD DOMINION FREIGHT LINE INC&nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DBAName">DBA Name:</A></TH>
       <TD class="queryfield" valign=top colspan=3>&nbsp;</TD>
     </TR>
         
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PhysicalAddress">Physical Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="physicaladdressvalue">
        500 OLD DOMINION WAY<br>
            THOMASVILLE, NC &nbsp; 27360-8923
         &nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#Phone">Phone:</A></TH>
       <TD class="queryfield" valign=top colspan=3>
       (800) 235-5569
        &nbsp;</TD>
    </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#MailingAddress">Mailing Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="mailingaddressvalue">
        500 OLD DOMINION WAY<br>
          THOMASVILLE, NC &nbsp; 27360-8923
         &nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DUNSNumber">DUNS Number:</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>68-708-77  &nbsp;</TD>
     </TR>
     <TR>
      <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PowerUnits">Power Units:</A></TH>
      <TD class="queryfield" valign=top>10,313&nbsp;</TD>
      <TD colspan=2 style="padding: 0;">
         <TABLE border=0 WIDTH=100% cellpadding=2 cellspacing=0>
          <!-- IST-599 add non-cmv total -->
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#NonCMV">Non-CMV Units:</A></TH>
          <TD class="queryfield" valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;">0&nbsp;</TD>
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#Drivers">Drivers:</A></TH>
          <TD valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><FONT style=font-size:80% face=arial color=#0000C0><B>10,341&nbsp;</TD>
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
                   <TD width=5% class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>General Freight</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Household Goods</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
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
                   <TD class="queryfield">X</TD>
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
                   <TD width=5% class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Liquids/Gases</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
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
                   <TD width=5% class="queryfield">X</TD>
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
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Beverages</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Paper Products</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Utilities</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Agricultural/Farm Supplies</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Construction</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Water Well</FONT></TD>
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
     10/21/2026</FONT></B><br>
     <br>
     Total Inspections: <FONT color="#0000C0">4382</FONT><br>
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
       <TD align="center" class="queryfield">2779</TD>
       <TD align="center" class="queryfield">4369</TD>
       <TD align="center" class="queryfield">1384</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service</TH>
       <TD align="center" class="queryfield">226</TD>
       <TD align="center" class="queryfield">25</TD>
       <TD align="center" class="queryfield">23</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service %</TH>
       <TD align="center" class="queryfield">
         8.1%
       </TD>
       <TD align="center" class="queryfield">
         0.6%
       </TD>
       <TD align="center" class="queryfield">
         1.7%
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
       <TD align="center" class="queryfield">19</TD>
       <TD align="center" class="queryfield">182</TD>
       <TD align="center" class="queryfield">347</TD>
       <TD align="center" class="queryfield">548</TD>
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
   10/21/2026</FONT></B><br>
   <br>
   Total inspections: <FONT color="#0000C0">25</FONT><br>
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
       <TD align="center" class="queryfield">9</TD>
       <TD align="center" class="queryfield">12</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service</TH>
       <TD align="center" class="queryfield">5</TD>
       <TD align="center" class="queryfield">5</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service %</TH>
       <TD align="center" class="queryfield">
         55.6%
       </TD>
       <TD align="center" class="queryfield">
         41.7%
       </TD>
     </TR>
   </TABLE>
 </CENTER>
 <br>
 <br>
 <!--  BEGIN: Crash Data -->
 <FONT size="2" face="arial">
   <B>Crashes results for 24 months prior to:
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
       <TD width=30% class="queryfield">09/29/1995 </TD>
       <TH SCOPE="ROW" width=20% class="querylabelbkg">Review Date:</TH>
       <TD width=30% class="queryfield">02/09/2023 </TD>
       </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg">Rating:</TH>
       <TD class="queryfield">Satisfactory </TD>
       <TH SCOPE="ROW" class="querylabelbkg">Type:</TH>
       <TD class="queryfield">Non-Ratable </TD>
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

QUERY: n_dotno = 90849, s_prefix = MC, pv_vpath = LIVIEW (retrieved 2026-10-23T21:57:14Z). 2 record text lines found.

- As shown: Docket Number:
- As shown: Legal Name:

Source. FMCSA Licensing and Insurance carrier search, USDOT 90849
- Query URL: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=90849&s_prefix=MC&pv_vpath=LIVIEW
- Retrieved (UTC): 2026-10-23T21:57:14Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:57:17 GMT
Content-Type: text/html; charset=WINDOWS-1252
strict-transport-security: max-age=31536000
content-language: en
server: 
x-frame-options: SAMEORIGIN
content-security-policy: frame-ancestors 'self';
Connection: close
Content-Length: 17590

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
              <input type="text" id="usdot_number" NAME="n_dotno" value="90849" MAXLENGTH="8" size="27">
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
<SPAN class="footer_title_text" align="left"> October 23, 2026</SPAN>
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

## SCHNEIDER NATIONAL CARRIERS INC (carrier, USDOT 264184)

### Fields that matter

| Field | Value as shown |
| --- | --- |
| census.record_count | 1 |
| census.dot_number | 264184 |
| census.legal_name | SCHNEIDER NATIONAL CARRIERS INC |
| census.dba_name | not present in the record |
| census.phy_city | GREEN BAY |
| census.phy_state | WI |
| census.power_units | 9866 |
| census.total_drivers | 11335 |
| census.docket1prefix | MC |
| census.docket1 | 133655 |
| census.docket1_status_code | A |
| census.safety_rating | S |
| census.safety_rating_date | 20030220 |
| census.mcs150_mileage | 847225359 |
| census.mcs150_mileage_year | 2025 |
| census.mcs150_date | 20260130 |
| census.business_org_desc | CORPORATION |
| census.carship | C;T;S;B |
| census.carrier_operation | A |
| census.status_code | A |
| census.classdef | AUTHORIZED FOR HIRE |
| safer.Entity Type: | CARRIER/SHIPPER/CARGO TANK/BROKER |
| safer.USDOT Status: | ACTIVE |
| safer.Out of Service Date: | None |
| safer.USDOT Number: | 264184 |
| safer.MCS-150 Form Date: | 01/30/2026 |
| safer.MCS-150 Mileage (Year): | 847,225,359 (2025) |
| safer.Operating Authority Status: | AUTHORIZED FOR: Broker of Household Goods Motor Carrier of Property (Except Household Goods) Broker of Property (Except Household Goods) |
| safer.MC/MX/FF Number(s): | MC-133655 |
| safer.Legal Name: | SCHNEIDER NATIONAL CARRIERS INC |
| safer.DBA Name: | none shown (blank in the source) |
| safer.Physical Address: | 3101 SOUTH PACKERLAND DRIVE GREEN BAY, WI   54313 |
| safer.Phone: | (800) 558-6767 |
| safer.Power Units: | 9,866 |
| safer.Non-CMV Units: | 0 |
| safer.Drivers: | 11,335 |
| safer.Total Inspections: | label not found in the response text |
| safer.Rating Date: | 02/20/2003 |
| safer.Review Date: | 04/06/2023 |
| safer.Rating: | Satisfactory |
| li.record_lines | Docket Number:, Legal Name: |

### Source evidence

### Census record (FMCSA Company Census File, DOT open data dataset az4n-8mr2)

QUERY: dot_number = 264184 returned 1 record (retrieved 2026-10-23T21:57:16Z).

- dot_number as shown: 264184
- legal_name as shown: SCHNEIDER NATIONAL CARRIERS INC
- dba_name: not present in the record
- phy_city as shown: GREEN BAY
- phy_state as shown: WI
- power_units as shown: 9866
- total_drivers as shown: 11335
- docket1prefix as shown: MC
- docket1 as shown: 133655
- docket1_status_code as shown: A
- safety_rating as shown: S
- safety_rating_date as shown: 20030220
- mcs150_mileage as shown: 847225359
- mcs150_mileage_year as shown: 2025
- mcs150_date as shown: 20260130
- business_org_desc as shown: CORPORATION
- carship as shown: C;T;S;B
- carrier_operation as shown: A
- status_code as shown: A
- classdef as shown: AUTHORIZED FOR HIRE

Source. FMCSA Company Census File record, USDOT 264184
- Query URL: https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=264184&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef
- Retrieved (UTC): 2026-10-23T21:57:16Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Server: nginx
Date: Fri, 23 Oct 2026 21:57:18 GMT
Content-Type: application/json;charset=utf-8
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Socrata-RequestId: e5d3786f28210014341628493a4b6359
Access-Control-Allow-Origin: *
ETag: W/"aW5kaWEuMzM1NTNfNF8xMDQxd3N2eG9UcUt5ZmFKaWpkZlM3eFExcXZXV2k4---gzips4IZONH3rbmIKvhKPsd6Z-w3v-Y--gzip--gzip"
X-SODA2-Fields: ["dot_number","legal_name","dba_name","phy_city","phy_state","power_units","total_drivers","docket1prefix","docket1","docket1_status_code","safety_rating","safety_rating_date","mcs150_mileage","mcs150_mileage_year","mcs150_date","business_org_desc","carship","carrier_operation","status_code","classdef"]
X-SODA2-Types: ["number","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text"]
X-SODA2-Data-Out-Of-Date: false
X-SODA2-Truth-Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
X-SODA2-Secondary-Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
Vary: Accept-Encoding
X-Socrata-Region: aws-us-east-1-fedramp-prod
Connection: close
Transfer-Encoding: chunked

[{"dot_number":"264184","legal_name":"SCHNEIDER NATIONAL CARRIERS INC","phy_city":"GREEN BAY","phy_state":"WI","power_units":"9866","total_drivers":"11335","docket1prefix":"MC","docket1":"133655","docket1_status_code":"A","safety_rating":"S","safety_rating_date":"20030220","mcs150_mileage":"847225359","mcs150_mileage_year":"2025","mcs150_date":"20260130","business_org_desc":"CORPORATION","carship":"C;T;S;B","carrier_operation":"A","status_code":"A","classdef":"AUTHORIZED FOR HIRE"}]

```

### SAFER Company Snapshot

QUERY: query_param = USDOT, query_string = 264184 (retrieved 2026-10-23T21:57:17Z). 18 of 19 labelled fields were found in the page text. Each value below is the text that follows its label in the page; the inspection, out of service and crash tables are not parsed and are read from the complete page beneath the source link.

- Entity Type: CARRIER/SHIPPER/CARGO TANK/BROKER
- USDOT Status: ACTIVE
- Out of Service Date: None
- USDOT Number: 264184
- MCS-150 Form Date: 01/30/2026
- MCS-150 Mileage (Year): 847,225,359 (2025)
- Operating Authority Status: AUTHORIZED FOR: Broker of Household Goods Motor Carrier of Property (Except Household Goods) Broker of Property (Except Household Goods)
- MC/MX/FF Number(s): MC-133655
- Legal Name: SCHNEIDER NATIONAL CARRIERS INC
- DBA Name: none shown (blank in the source)
- Physical Address: 3101 SOUTH PACKERLAND DRIVE GREEN BAY, WI   54313
- Phone: (800) 558-6767
- Power Units: 9,866
- Non-CMV Units: 0
- Drivers: 11,335
- Total Inspections: label not found in the response text
- Rating Date: 02/20/2003
- Review Date: 04/06/2023
- Rating: Satisfactory

Source. FMCSA SAFER Company Snapshot, USDOT 264184
- Query URL: https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=264184
- Retrieved (UTC): 2026-10-23T21:57:17Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:57:19 GMT
Content-Type: text/html
referrer-policy: strict-origin
content-security-policy: frame-ancestors 'self';
set-cookie: AWSALB=vGc27zLbMZkImgENP/r0xAPK+P0mSiO0QvXX2XGlsUo30HSJ4MAgkg9otXeXYD3vfk13+yNJyOhxvfLpXZUvBjzyQeSOUPLGtvPpa8qG9znJEErZuQv9q9SVeh78; Expires=Fri, 30 Oct 2026 21:57:19 GMT; Path=/
set-cookie: AWSALBCORS=vGc27zLbMZkImgENP/r0xAPK+P0mSiO0QvXX2XGlsUo30HSJ4MAgkg9otXeXYD3vfk13+yNJyOhxvfLpXZUvBjzyQeSOUPLGtvPpa8qG9znJEErZuQv9q9SVeh78; Expires=Fri, 30 Oct 2026 21:57:19 GMT; Path=/; SameSite=None; Secure
set-cookie: ASPSESSIONIDQESRRADS=APCPOILBBJJJPEIACNKBKCNE; secure; path=/
cache-control: private
server: Microsoft-IIS/10.0
x-powered-by: ASP.NET
x-frame-options: SAMEORIGIN
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-xss-protection: 1; mode=block
x-content-type-options: nosniff
Connection: close
Content-Length: 46234


<noscript>
This page requires scripting to be enabled.
</noscript>
<noscript>
This page requires scripting to be enabled.
</noscript>

<HTML>
 <HEAD>
  <TITLE>SAFER Web - Company Snapshot SCHNEIDER NATIONAL CARRIERS INC</TITLE>
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
    <!--td>LAST QUERY STRING:264184 </TD-->
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
    <TD COLSPAN="3" ALIGN="CENTER"><LABEL for="4">Enter Value:</LABEL>&nbsp;<input id="4"type=" text" name="query_string" value="264184">
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
                          <B>SCHNEIDER NATIONAL CARRIERS INC</B><br>
                          USDOT Number: 264184<br>
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
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://ai.fmcsa.dot.gov/sms/safer_xfr.aspx?DOT=264184&Form=SAFER" onMouseover="return true">SMS Results</A></FONT></TD>
                             </TR><TR>
                               <TD align=right><IMG src="Images/bullet_hp.gif" alt="" width=50% height=10></TD>
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://motus.dot.gov/customer/264184/account">Licensing & Insurance</A></FONT>
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
                       10/21/2026. </B><br>
                       
                          <br>
                          <B>To find out if this entity has a pending insurance cancellation, please <A href="http://motus.dot.gov/customer/264184/account">click here</A>.</B>
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
         CARRIER/SHIPPER/CARGO TANK/BROKER
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
       <TD class="queryfield" valign=top>264184&nbsp;</TD>
       <TH class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#StateID">State Carrier ID Number:</A></TH>
       <TD class="queryfield" valign=top>&nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Form Date:</A></TH>
       <TD class="queryfield" valign=top>01/30/2026&nbsp;</TD>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Mileage (Year):</A></TH>
       <TD valign=top><FONT style=font-size:80% face=arial color=#0000C0><B>847,225,359 (2025)&nbsp;</TD>
     </TR>



     
     <tr>
       <!-- BEGIN: OPERATING AUTHORITY INFORMATION -->
       <td colspan="4" class="querylabelbkg" style="text-align:center">OPERATING AUTHORITY INFORMATION</td>
</tr>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#OOS">Operating Authority Status:</A></TH>
       
       <TD  colspan="4"  width=30% class="queryfield">AUTHORIZED FOR: <br> Broker of Household Goods <br>  Motor Carrier of Property (Except Household Goods) <br>  Broker of Property (Except Household Goods) <br>  Motor Carrier of Household Goods <br><br> <b style="color:black">For Licensing and Insurance details </b> <a  style="color:#0000c0" href="http://motus.dot.gov/customer/264184/account">click here.</a></TD>
       

     </TR>
          <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#ICCNumbers">MC/MX/FF Number(s):</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>
         
         <A href="http://motus.dot.gov/customer/264184/account"> MC-133655</A><br>
         
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
       <TD class="queryfield" valign=top colspan=3>SCHNEIDER NATIONAL CARRIERS INC&nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DBAName">DBA Name:</A></TH>
       <TD class="queryfield" valign=top colspan=3>&nbsp;</TD>
     </TR>
         
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PhysicalAddress">Physical Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="physicaladdressvalue">
        3101 SOUTH PACKERLAND DRIVE<br>
            GREEN BAY, WI &nbsp; 54313
         &nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#Phone">Phone:</A></TH>
       <TD class="queryfield" valign=top colspan=3>
       (800) 558-6767
        &nbsp;</TD>
    </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#MailingAddress">Mailing Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="mailingaddressvalue">
        PO BOX 2545<br>
          GREEN BAY, WI &nbsp; 54306
         &nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DUNSNumber">DUNS Number:</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>15-730-4676&nbsp;</TD>
     </TR>
     <TR>
      <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PowerUnits">Power Units:</A></TH>
      <TD class="queryfield" valign=top>9,866&nbsp;</TD>
      <TD colspan=2 style="padding: 0;">
         <TABLE border=0 WIDTH=100% cellpadding=2 cellspacing=0>
          <!-- IST-599 add non-cmv total -->
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#NonCMV">Non-CMV Units:</A></TH>
          <TD class="queryfield" valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;">0&nbsp;</TD>
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#Drivers">Drivers:</A></TH>
          <TD valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><FONT style=font-size:80% face=arial color=#0000C0><B>11,335&nbsp;</TD>
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
                   <TD width=5% class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>General Freight</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Household Goods</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Metal: sheets, coils, rolls</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Motor Vehicles</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Drive/Tow away</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
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
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Machinery, Large Objects</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Fresh Produce</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Liquids/Gases</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
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
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>US Mail</FONT></TD>
                 </TR>
               </TABLE>
             </TD>
             <TD width=32% valign=top>
               <TABLE border=0 cellpadding=2 cellspacing=0 summary="For formatting purpose">
                 <TR><TH SCOPE="COL"><div class="hidden">SAFER Layout</div></TH>
                 </TR>
                 <TR>
                   <TD width=5% class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Chemicals</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Commodities Dry Bulk</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Refrigerated Food</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Beverages</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Paper Products</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Utilities</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Agricultural/Farm Supplies</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield">X</TD>
                   <TD><FONT style=font-size:80% face=arial>Construction</FONT></TD>
                 </TR>
                 <TR>
                   <TD class="queryfield"></TD>
                   <TD><FONT style=font-size:80% face=arial>Water Well</FONT></TD>
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
     10/21/2026</FONT></B><br>
     <br>
     Total Inspections: <FONT color="#0000C0">15070</FONT><br>
     Total IEP Inspections: <FONT color="#0000C0">2</FONT><br>
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
       <TD align="center" class="queryfield">8415</TD>
       <TD align="center" class="queryfield">15067</TD>
       <TD align="center" class="queryfield">499</TD>
       <TD align="center" class="queryfield">2</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service</TH>
       <TD align="center" class="queryfield">1511</TD>
       <TD align="center" class="queryfield">90</TD>
       <TD align="center" class="queryfield">5</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service %</TH>
       <TD align="center" class="queryfield">
         18%
       </TD>
       <TD align="center" class="queryfield">
         0.6%
       </TD>
       <TD align="center" class="queryfield">
         1%
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
       <TD align="center" class="queryfield">10</TD>
       <TD align="center" class="queryfield">218</TD>
       <TD align="center" class="queryfield">471</TD>
       <TD align="center" class="queryfield">699</TD>
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
   10/21/2026</FONT></B><br>
   <br>
   Total inspections: <FONT color="#0000C0">2</FONT><br>
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
       <TD align="center" class="queryfield">2</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service</TH>
       <TD align="center" class="queryfield">0</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service %</TH>
       <TD align="center" class="queryfield">
         18%
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
       <TD width=30% class="queryfield">02/20/2003 </TD>
       <TH SCOPE="ROW" width=20% class="querylabelbkg">Review Date:</TH>
       <TD width=30% class="queryfield">04/06/2023 </TD>
       </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg">Rating:</TH>
       <TD class="queryfield">Satisfactory </TD>
       <TH SCOPE="ROW" class="querylabelbkg">Type:</TH>
       <TD class="queryfield">Non-Ratable </TD>
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

QUERY: n_dotno = 264184, s_prefix = MC, pv_vpath = LIVIEW (retrieved 2026-10-23T21:57:18Z). 2 record text lines found.

- As shown: Docket Number:
- As shown: Legal Name:

Source. FMCSA Licensing and Insurance carrier search, USDOT 264184
- Query URL: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=264184&s_prefix=MC&pv_vpath=LIVIEW
- Retrieved (UTC): 2026-10-23T21:57:18Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:57:20 GMT
Content-Type: text/html; charset=WINDOWS-1252
strict-transport-security: max-age=31536000
content-language: en
server: 
x-frame-options: SAMEORIGIN
content-security-policy: frame-ancestors 'self';
Connection: close
Content-Length: 17591

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
              <input type="text" id="usdot_number" NAME="n_dotno" value="264184" MAXLENGTH="8" size="27">
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
<SPAN class="footer_title_text" align="left"> October 23, 2026</SPAN>
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

## XPO LOGISTICS FREIGHT INC (carrier, USDOT 241829)

### Fields that matter

| Field | Value as shown |
| --- | --- |
| census.record_count | 1 |
| census.dot_number | 241829 |
| census.legal_name | XPO LOGISTICS FREIGHT INC |
| census.dba_name | not present in the record |
| census.phy_city | ANN ARBOR |
| census.phy_state | MI |
| census.power_units | 20208 |
| census.total_drivers | 13358 |
| census.docket1prefix | MC |
| census.docket1 | 165377 |
| census.docket1_status_code | A |
| census.safety_rating | S |
| census.safety_rating_date | 19941222 |
| census.mcs150_mileage | 849996482 |
| census.mcs150_mileage_year | 2026 |
| census.mcs150_date | 20260928 |
| census.business_org_desc | CORPORATION |
| census.carship | C;S;B |
| census.carrier_operation | A |
| census.status_code | A |
| census.classdef | AUTHORIZED FOR HIRE |
| safer.Entity Type: | CARRIER/SHIPPER/BROKER |
| safer.USDOT Status: | ACTIVE |
| safer.Out of Service Date: | None |
| safer.USDOT Number: | 241829 |
| safer.MCS-150 Form Date: | 09/28/2026 |
| safer.MCS-150 Mileage (Year): | 849,996,482 (2026) |
| safer.Operating Authority Status: | AUTHORIZED FOR: Motor Carrier of Property (Except Household Goods) Broker of Property (Except Household Goods) |
| safer.MC/MX/FF Number(s): | COMPANY INFORMATION |
| safer.Legal Name: | XPO LOGISTICS FREIGHT INC |
| safer.DBA Name: | none shown (blank in the source) |
| safer.Physical Address: | 2211 OLD EARHART RD ANN ARBOR, MI   48105-2963 |
| safer.Phone: | (734) 757-1667 |
| safer.Power Units: | 10,104 |
| safer.Non-CMV Units: | 10,104 |
| safer.Drivers: | 13,358 |
| safer.Total Inspections: | label not found in the response text |
| safer.Rating Date: | 12/22/1994 |
| safer.Review Date: | 10/18/2023 |
| safer.Rating: | Satisfactory |
| li.record_lines | Docket Number:, Legal Name: |

### Source evidence

### Census record (FMCSA Company Census File, DOT open data dataset az4n-8mr2)

QUERY: dot_number = 241829 returned 1 record (retrieved 2026-10-23T21:57:19Z).

- dot_number as shown: 241829
- legal_name as shown: XPO LOGISTICS FREIGHT INC
- dba_name: not present in the record
- phy_city as shown: ANN ARBOR
- phy_state as shown: MI
- power_units as shown: 20208
- total_drivers as shown: 13358
- docket1prefix as shown: MC
- docket1 as shown: 165377
- docket1_status_code as shown: A
- safety_rating as shown: S
- safety_rating_date as shown: 19941222
- mcs150_mileage as shown: 849996482
- mcs150_mileage_year as shown: 2026
- mcs150_date as shown: 20260928
- business_org_desc as shown: CORPORATION
- carship as shown: C;S;B
- carrier_operation as shown: A
- status_code as shown: A
- classdef as shown: AUTHORIZED FOR HIRE

Source. FMCSA Company Census File record, USDOT 241829
- Query URL: https://data.transportation.gov/resource/az4n-8mr2.json?dot_number=241829&$select=dot_number,legal_name,dba_name,phy_city,phy_state,power_units,total_drivers,docket1prefix,docket1,docket1_status_code,safety_rating,safety_rating_date,mcs150_mileage,mcs150_mileage_year,mcs150_date,business_org_desc,carship,carrier_operation,status_code,classdef
- Retrieved (UTC): 2026-10-23T21:57:19Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Server: nginx
Date: Fri, 23 Oct 2026 21:57:21 GMT
Content-Type: application/json;charset=utf-8
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Socrata-RequestId: 247d249d07d099d9156740d83c779de0
Access-Control-Allow-Origin: *
ETag: W/"aW5kaWEuMzM1NTNfNF8xMDQxSUpFMDFUS0RwT09NMWZhMDNlOEdjR2VKNjlZ---gzipscVkD8emrIESzgtz6TDsA4KhwOk--gzip--gzip"
X-SODA2-Fields: ["dot_number","legal_name","dba_name","phy_city","phy_state","power_units","total_drivers","docket1prefix","docket1","docket1_status_code","safety_rating","safety_rating_date","mcs150_mileage","mcs150_mileage_year","mcs150_date","business_org_desc","carship","carrier_operation","status_code","classdef"]
X-SODA2-Types: ["number","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text","text"]
X-SODA2-Data-Out-Of-Date: false
X-SODA2-Truth-Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
X-SODA2-Secondary-Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
Last-Modified: Fri, 23 Oct 2026 10:31:13 GMT
Vary: Accept-Encoding
X-Socrata-Region: aws-us-east-1-fedramp-prod
Connection: close
Transfer-Encoding: chunked

[{"dot_number":"241829","legal_name":"XPO LOGISTICS FREIGHT INC","phy_city":"ANN ARBOR","phy_state":"MI","power_units":"20208","total_drivers":"13358","docket1prefix":"MC","docket1":"165377","docket1_status_code":"A","safety_rating":"S","safety_rating_date":"19941222","mcs150_mileage":"849996482","mcs150_mileage_year":"2026","mcs150_date":"20260928","business_org_desc":"CORPORATION","carship":"C;S;B","carrier_operation":"A","status_code":"A","classdef":"AUTHORIZED FOR HIRE"}]

```

### SAFER Company Snapshot

QUERY: query_param = USDOT, query_string = 241829 (retrieved 2026-10-23T21:57:21Z). 18 of 19 labelled fields were found in the page text. Each value below is the text that follows its label in the page; the inspection, out of service and crash tables are not parsed and are read from the complete page beneath the source link.

- Entity Type: CARRIER/SHIPPER/BROKER
- USDOT Status: ACTIVE
- Out of Service Date: None
- USDOT Number: 241829
- MCS-150 Form Date: 09/28/2026
- MCS-150 Mileage (Year): 849,996,482 (2026)
- Operating Authority Status: AUTHORIZED FOR: Motor Carrier of Property (Except Household Goods) Broker of Property (Except Household Goods)
- MC/MX/FF Number(s): COMPANY INFORMATION
- Legal Name: XPO LOGISTICS FREIGHT INC
- DBA Name: none shown (blank in the source)
- Physical Address: 2211 OLD EARHART RD ANN ARBOR, MI   48105-2963
- Phone: (734) 757-1667
- Power Units: 10,104
- Non-CMV Units: 10,104
- Drivers: 13,358
- Total Inspections: label not found in the response text
- Rating Date: 12/22/1994
- Review Date: 10/18/2023
- Rating: Satisfactory

Source. FMCSA SAFER Company Snapshot, USDOT 241829
- Query URL: https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&query_type=queryCarrierSnapshot&query_param=USDOT&query_string=241829
- Retrieved (UTC): 2026-10-23T21:57:21Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:57:23 GMT
Content-Type: text/html
referrer-policy: strict-origin
content-security-policy: frame-ancestors 'self';
set-cookie: AWSALB=MKZUuuBsIwN63bw4Kx40jVE9fQRwNTwHgqW41FFTtgcrRj56Id/WwcZxq5Wz1dvyDwKDyWWYA1g7Xqh+74GX2KYNLIT4FosvDzmp344eQLRAyWGzyonLKNRBvivi; Expires=Fri, 30 Oct 2026 21:57:23 GMT; Path=/
set-cookie: AWSALBCORS=MKZUuuBsIwN63bw4Kx40jVE9fQRwNTwHgqW41FFTtgcrRj56Id/WwcZxq5Wz1dvyDwKDyWWYA1g7Xqh+74GX2KYNLIT4FosvDzmp344eQLRAyWGzyonLKNRBvivi; Expires=Fri, 30 Oct 2026 21:57:23 GMT; Path=/; SameSite=None; Secure
set-cookie: ASPSESSIONIDSGRRQABS=AFBJFDOBGJKNNPMOLAMPMMDN; secure; path=/
cache-control: private
server: Microsoft-IIS/10.0
x-powered-by: ASP.NET
x-frame-options: SAMEORIGIN
strict-transport-security: max-age=31536000; includeSubDomains; preload
x-xss-protection: 1; mode=block
x-content-type-options: nosniff
Connection: close
Content-Length: 45782


<noscript>
This page requires scripting to be enabled.
</noscript>
<noscript>
This page requires scripting to be enabled.
</noscript>

<HTML>
 <HEAD>
  <TITLE>SAFER Web - Company Snapshot XPO LOGISTICS FREIGHT INC</TITLE>
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
    <!--td>LAST QUERY STRING:241829 </TD-->
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
    <TD COLSPAN="3" ALIGN="CENTER"><LABEL for="4">Enter Value:</LABEL>&nbsp;<input id="4"type=" text" name="query_string" value="241829">
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
                          <B>XPO LOGISTICS FREIGHT INC</B><br>
                          USDOT Number: 241829<br>
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
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://ai.fmcsa.dot.gov/sms/safer_xfr.aspx?DOT=241829&Form=SAFER" onMouseover="return true">SMS Results</A></FONT></TD>
                             </TR><TR>
                               <TD align=right><IMG src="Images/bullet_hp.gif" alt="" width=50% height=10></TD>
                               <TD align=left><FONT style=font-size:80% face=arial><A href="http://motus.dot.gov/customer/241829/account">Licensing & Insurance</A></FONT>
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
                       10/21/2026. </B><br>
                       
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
         CARRIER/SHIPPER/BROKER
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
       <TD class="queryfield" valign=top>241829&nbsp;</TD>
       <TH class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#StateID">State Carrier ID Number:</A></TH>
       <TD class="queryfield" valign=top>&nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Form Date:</A></TH>
       <TD class="queryfield" valign=top>09/28/2026&nbsp;</TD>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#">MCS-150 Mileage (Year):</A></TH>
       <TD valign=top><FONT style=font-size:80% face=arial color=#0000C0><B>849,996,482 (2026)&nbsp;</TD>
     </TR>



     
     <tr>
       <!-- BEGIN: OPERATING AUTHORITY INFORMATION -->
       <td colspan="4" class="querylabelbkg" style="text-align:center">OPERATING AUTHORITY INFORMATION</td>
</tr>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#OOS">Operating Authority Status:</A></TH>
       
       <TD  colspan="4"  width=30% class="queryfield">AUTHORIZED FOR: <br> Motor Carrier of Property (Except Household Goods) <br>  Broker of Property (Except Household Goods) <br><br> <b style="color:black">For Licensing and Insurance details </b> <a  style="color:#0000c0" href="http://motus.dot.gov/customer/241829/account">click here.</a></TD>
       

     </TR>
          <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#ICCNumbers">MC/MX/FF Number(s):</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>
         
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
       <TD class="queryfield" valign=top colspan=3>XPO LOGISTICS FREIGHT INC&nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DBAName">DBA Name:</A></TH>
       <TD class="queryfield" valign=top colspan=3>&nbsp;</TD>
     </TR>
         
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PhysicalAddress">Physical Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="physicaladdressvalue">
        2211 OLD EARHART RD<br>
            ANN ARBOR, MI &nbsp; 48105-2963
         &nbsp;</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#Phone">Phone:</A></TH>
       <TD class="queryfield" valign=top colspan=3>
       (734) 757-1667
        &nbsp;</TD>
    </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#MailingAddress">Mailing Address:</A></TH>
       <TD class="queryfield" valign=top colspan=3 id="mailingaddressvalue">
        2211 OLD EARHART ROAD<br>
          ANN ARBOR, MI &nbsp; 48105-2751
         &nbsp;</TD>
     </TR>

     <TR>
       <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#DUNSNumber">DUNS Number:</A></TH>
       <TD  colspan="4"  class="queryfield" valign=top>80-431-863 &nbsp;</TD>
     </TR>
     <TR>
      <TH SCOPE="ROW" class="querylabelbkg" align=right><A class="querylabel" href="saferhelp.aspx#PowerUnits">Power Units:</A></TH>
      <TD class="queryfield" valign=top>10,104&nbsp;</TD>
      <TD colspan=2 style="padding: 0;">
         <TABLE border=0 WIDTH=100% cellpadding=2 cellspacing=0>
          <!-- IST-599 add non-cmv total -->
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#NonCMV">Non-CMV Units:</A></TH>
          <TD class="queryfield" valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;">10,104&nbsp;</TD>
          <TH SCOPE="ROW" class="querylabelbkg" align=right style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><A class="querylabel" href="saferhelp.aspx#Drivers">Drivers:</A></TH>
          <TD valign=top style="border-left: silver; border-right: silver; border-style: solid; border-top: none; border-bottom: none;"><FONT style=font-size:80% face=arial color=#0000C0><B>13,358&nbsp;</TD>
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
                   <TD width=5% class="queryfield">X</TD>
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
                   <TD width=5% class="queryfield">X</TD>
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
                   <TD width=5% class="queryfield">X</TD>
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
                   <TD class="queryfield">BIT</TD>
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
     10/21/2026</FONT></B><br>
     <br>
     Total Inspections: <FONT color="#0000C0">4708</FONT><br>
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
       <TD align="center" class="queryfield">3109</TD>
       <TD align="center" class="queryfield">4681</TD>
       <TD align="center" class="queryfield">1345</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service</TH>
       <TD align="center" class="queryfield">390</TD>
       <TD align="center" class="queryfield">36</TD>
       <TD align="center" class="queryfield">26</TD>
       <TD align="center" class="queryfield">0</TD>
     </TR>
     <TR>
       <TH SCOPE="ROW" align="right" class="querylabelbkg">Out of Service %</TH>
       <TD align="center" class="queryfield">
         12.5%
       </TD>
       <TD align="center" class="queryfield">
         0.8%
       </TD>
       <TD align="center" class="queryfield">
         1.9%
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
       <TD align="center" class="queryfield">16</TD>
       <TD align="center" class="queryfield">188</TD>
       <TD align="center" class="queryfield">411</TD>
       <TD align="center" class="queryfield">615</TD>
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
   10/21/2026</FONT></B><br>
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
   <FONT color="#0000C0">10/21/2026</FONT></B><br>
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
       <TD width=30% class="queryfield">12/22/1994 </TD>
       <TH SCOPE="ROW" width=20% class="querylabelbkg">Review Date:</TH>
       <TD width=30% class="queryfield">10/18/2023 </TD>
       </TR>
     <TR>
       <TH SCOPE="ROW" class="querylabelbkg">Rating:</TH>
       <TD class="queryfield">Satisfactory </TD>
       <TH SCOPE="ROW" class="querylabelbkg">Type:</TH>
       <TD class="queryfield">Non-Ratable </TD>
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

QUERY: n_dotno = 241829, s_prefix = MC, pv_vpath = LIVIEW (retrieved 2026-10-23T21:57:22Z). 2 record text lines found.

- As shown: Docket Number:
- As shown: Legal Name:

Source. FMCSA Licensing and Insurance carrier search, USDOT 241829
- Query URL: https://li-public.fmcsa.dot.gov/LIVIEW/pkg_carrquery.prc_carrlist?n_dotno=241829&s_prefix=MC&pv_vpath=LIVIEW
- Retrieved (UTC): 2026-10-23T21:57:22Z
Excerpt (complete raw HTTP response transcript for the query above: status line, headers in the order returned, a blank line, then the complete body exactly as returned):
```
HTTP/1.1 200 OK
Date: Fri, 23 Oct 2026 21:57:24 GMT
Content-Type: text/html; charset=WINDOWS-1252
strict-transport-security: max-age=31536000
content-language: en
server: 
x-frame-options: SAMEORIGIN
content-security-policy: frame-ancestors 'self';
Connection: close
Content-Length: 17591

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
              <input type="text" id="usdot_number" NAME="n_dotno" value="241829" MAXLENGTH="8" size="27">
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
<SPAN class="footer_title_text" align="left"> October 23, 2026</SPAN>
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

## Peloton Tread+ (product)

### Fields that matter

| Field | Value as shown |
| --- | --- |
| recall_numbers | 21128 |
| query.RecallNumber=21-128.record_count | 1 |
| query.ProductName=Tread+.record_count | 1 |

### Source evidence

### Recall number query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128
Retrieved (UTC): 2026-10-23T21:57:24Z

CPSC returned 1 record(s) for this query.

- Returned candidate: recall "21128"; product name(s) as shown: "Tread+".

#### Recall 21-128
- Recall number as shown: "21128"
- Announcement date as shown: "2021-05-05T00:00:00" (May 5, 2021)
- Title as shown: "Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported"
- Product as shown: "Tread+"
- Hazard as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Remedy as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Units as shown: "About 125,000"
- Remedy options as shown: "Refund"; "Repair"
- CPSC recall page as shown: "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported"
- Note: the remedy text in this API record repeats the hazard text word for word. Read the remedy from the CPSC recall page above and quote that page as its own source.
- Listed above as: Returned candidate

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=21-128>
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Vary: Accept-Encoding
Cache-Control: no-cache
Expires: Fri, 23 Oct 2026 21:57:25 GMT
Date: Fri, 23 Oct 2026 21:57:25 GMT
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Alt-Svc: h3=":443"; ma=93600
Content-Length: 2735

[{"RecallID":9057,"RecallNumber":"21128","RecallDate":"2021-05-05T00:00:00","Description":"This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread+ model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.","URL":"https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported","Title":"Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported","ConsumerContact":"Peloton toll-free at 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.","LastPublishDate":"2021-05-05T00:00:00","Products":[{"Name":"Tread+","Description":"","Model":"","Type":"","CategoryID":"","NumberOfUnits":"About 125,000"}],"Inconjunctions":[],"Images":[{"URL":"https://www.cpsc.gov/s3fs-public/Peloton Tread Plus Recall Picture_0.png","Caption":"Recalled Peloton Tread+ Treadmill"}],"Injuries":[{"Name":"A 6-year-old child recently died after being pulled under the rear of the treadmill. In addition, Peloton has received 72 reports of adult users, children, pets and/or objects being pulled under the rear of the treadmill, including 29 reports of injuries to children such as second- and third-degree abrasions, broken bones, and lacerations."}],"Manufacturers":[],"Retailers":[{"Name":"Online at onepeloton.com and at Peloton showrooms from September 2018 through April 2021 for about $4,295.","CompanyID":""}],"Importers":[{"Name":"Peloton Interactive, Inc., of New York","CompanyID":""}],"Distributors":[],"SoldAtLabel":null,"ManufacturerCountries":[{"Country":"Taiwan"}],"ProductUPCs":[],"Hazards":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.","HazardType":"","HazardTypeID":""}],"Remedies":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."}],"RemedyOptions":[{"Option":"Refund"},{"Option":"Repair"}]}]
```

### Product query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Tread%2B
Retrieved (UTC): 2026-10-23T21:57:25Z

CPSC returned 1 record(s) for this query.

- Returned candidate: recall "21128"; product name(s) as shown: "Tread+".

#### Recall 21-128
- Recall number as shown: "21128"
- Announcement date as shown: "2021-05-05T00:00:00" (May 5, 2021)
- Title as shown: "Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported"
- Product as shown: "Tread+"
- Hazard as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Remedy as shown: "Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."
- Units as shown: "About 125,000"
- Remedy options as shown: "Refund"; "Repair"
- CPSC recall page as shown: "https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported"
- Note: the remedy text in this API record repeats the hazard text word for word. Read the remedy from the CPSC recall page above and quote that page as its own source.
- Listed above as: Returned candidate

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Tread%2B>
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Vary: Accept-Encoding
Cache-Control: no-cache
Expires: Fri, 23 Oct 2026 21:57:26 GMT
Date: Fri, 23 Oct 2026 21:57:26 GMT
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Alt-Svc: h3=":443"; ma=93600
Content-Length: 2735

[{"RecallID":9057,"RecallNumber":"21128","RecallDate":"2021-05-05T00:00:00","Description":"This recall involves the Peloton Tread+ treadmill with model number TR01. It has a running deck space of 67 inches, a 32-inch high definition (HD) touchscreen and a slatted belt. The treadmill was launched as the Peloton Tread in 2018 but renamed Tread+ in September 2020. The Tread+ model number TR01 is printed on a black sticker located on the end cap in the front of the treadmill deck. The treadmills have a touchscreen and are black with the Peloton logo on the monitor and the side rails. PLEASE NOTE: This product is different than the Peloton Tread that is also subject to a voluntary recall in cooperation with the CPSC on May 5, 2021 because the console on the Tread can detach and fall, posing a risk of injury to consumers.","URL":"https://www.cpsc.gov/Recalls/2021/Peloton-Recalls-Tread-Plus-Treadmills-After-One-Child-Died-and-More-than-70-Incidents-Reported","Title":"Peloton Recalls Tread+ Treadmills After One Child Died and More than 70 Incidents Reported","ConsumerContact":"Peloton toll-free at 844-410-0141 from 9 a.m. to 7 p.m. ET Monday through Friday, and 9 a.m. to 6:30 p.m. on weekends or online at www.onepeloton.com and click on Product Recalls at the bottom of the page for more information.","LastPublishDate":"2021-05-05T00:00:00","Products":[{"Name":"Tread+","Description":"","Model":"","Type":"","CategoryID":"","NumberOfUnits":"About 125,000"}],"Inconjunctions":[],"Images":[{"URL":"https://www.cpsc.gov/s3fs-public/Peloton Tread Plus Recall Picture_0.png","Caption":"Recalled Peloton Tread+ Treadmill"}],"Injuries":[{"Name":"A 6-year-old child recently died after being pulled under the rear of the treadmill. In addition, Peloton has received 72 reports of adult users, children, pets and/or objects being pulled under the rear of the treadmill, including 29 reports of injuries to children such as second- and third-degree abrasions, broken bones, and lacerations."}],"Manufacturers":[],"Retailers":[{"Name":"Online at onepeloton.com and at Peloton showrooms from September 2018 through April 2021 for about $4,295.","CompanyID":""}],"Importers":[{"Name":"Peloton Interactive, Inc., of New York","CompanyID":""}],"Distributors":[],"SoldAtLabel":null,"ManufacturerCountries":[{"Country":"Taiwan"}],"ProductUPCs":[],"Hazards":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death.","HazardType":"","HazardTypeID":""}],"Remedies":[{"Name":"Adult users, children, pets and objects can be pulled underneath the rear of the treadmill, posing a risk of injury or death."}],"RemedyOptions":[{"Option":"Refund"},{"Option":"Repair"}]}]
```

## Fisher-Price Rock 'n Play Sleeper (product)

### Fields that matter

| Field | Value as shown |
| --- | --- |
| recall_numbers | 19105 |
| query.RecallNumber=19-105.record_count | 1 |

### Source evidence

### Recall number query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=19-105
Retrieved (UTC): 2026-10-23T21:57:27Z

CPSC returned 1 record(s) for this query.

- Returned candidate: recall "19105"; product name(s) as shown: "All Models of Rock 'n Play Sleeper".

#### Recall 19-105
- Recall number as shown: "19105"
- Announcement date as shown: "2019-04-12T00:00:00" (April 12, 2019)
- Title as shown: "Fisher-Price Recalls Rock 'n Play Sleepers Due to Reports of Deaths"
- Product as shown: "All Models of Rock 'n Play Sleeper"
- Hazard as shown: "Infant fatalities have occurred in Rock 'n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances."
- Remedy as shown: "Consumers should immediately stop using the product and contact Fisher-Price for a refund or voucher."
- Units as shown: "About 4.7 million products"
- Remedy options: not present in the API record
- CPSC recall page as shown: "https://www.cpsc.gov/Recalls/2019/Fisher-Price-Recalls-Rock-n-Play-Sleepers-Due-to-Reports-of-Deaths"
- Listed above as: Returned candidate

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=19-105>
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Vary: Accept-Encoding
Cache-Control: no-cache
Expires: Fri, 23 Oct 2026 21:57:28 GMT
Date: Fri, 23 Oct 2026 21:57:28 GMT
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Alt-Svc: h3=":443"; ma=93600
Content-Length: 1747

[{"RecallID":8532,"RecallNumber":"19105","RecallDate":"2019-04-12T00:00:00","Description":"This recall involves all Rock 'n Play Sleepers.","URL":"https://www.cpsc.gov/Recalls/2019/Fisher-Price-Recalls-Rock-n-Play-Sleepers-Due-to-Reports-of-Deaths","Title":"Fisher-Price Recalls Rock 'n Play Sleepers Due to Reports of Deaths","ConsumerContact":"Fisher-Price online at www.service.mattel.com and click on “Recalls & Safety Alerts” or at 866-812-6518 from 9 a.m. to 6 p.m. ET Monday through Friday for more information.","LastPublishDate":"2019-04-12T00:00:00","Products":[{"Name":"All Models of Rock 'n Play Sleeper","Description":"","Model":"","Type":"","CategoryID":"","NumberOfUnits":"About 4.7 million products"}],"Inconjunctions":[],"Images":[{"URL":"https://www.cpsc.gov/s3fs-public/Fisher-Price Rock N Play_1.jpg","Caption":"Recalled Fisher-Price Rock 'n Play sleeper"}],"Injuries":[{"Name":"Since the 2009 product introduction, over 30 infant fatalities have occurred in Rock 'n Play Sleepers, after the infants rolled over while unrestrained, or under other circumstances."}],"Manufacturers":[],"Retailers":[{"Name":"Major retailers for approximately $40 to $149.","CompanyID":""}],"Importers":[{"Name":"Fisher-Price, of East Aurora, N.Y.","CompanyID":""}],"Distributors":[],"SoldAtLabel":null,"ManufacturerCountries":[{"Country":"China"}],"ProductUPCs":[],"Hazards":[{"Name":"Infant fatalities have occurred in Rock 'n Play Sleepers, after the infants rolled from their back to their stomach or side while unrestrained, or under other circumstances.","HazardType":"","HazardTypeID":""}],"Remedies":[{"Name":"Consumers should immediately stop using the product and contact Fisher-Price for a refund or voucher."}],"RemedyOptions":[]}]
```

## Vornado VH101 Personal Vortex electric space heaters (product)

### Fields that matter

| Field | Value as shown |
| --- | --- |
| recall_numbers | 18136 |
| query.RecallNumber=18-136.record_count | 1 |

### Source evidence

### Recall number query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=18-136
Retrieved (UTC): 2026-10-23T21:57:29Z

CPSC returned 1 record(s) for this query.

- Returned candidate: recall "18136"; product name(s) as shown: "VH101 Personal Vortex electric space heaters".

#### Recall 18-136
- Recall number as shown: "18136"
- Announcement date as shown: "2018-04-04T00:00:00" (April 4, 2018)
- Title as shown: "Vornado Air Recalls Electric Space Heaters Due to Fire and Burn Hazards"
- Product as shown: "VH101 Personal Vortex electric space heaters"
- Hazard as shown: "The electric space heater can overheat when in use, posing fire and burn hazards."
- Remedy as shown: "Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit, including free shipping."
- Units as shown: "About 350,000"
- Remedy options as shown: "Refund"; "Replace"
- CPSC recall page as shown: "https://www.cpsc.gov/Recalls/2018/Vornado-Air-Recalls-Electric-Space-Heaters-Due-to-Fire-and-Burn-Hazards"
- Listed above as: Returned candidate

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&RecallNumber=18-136>
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Vary: Accept-Encoding
Cache-Control: no-cache
Expires: Fri, 23 Oct 2026 21:57:30 GMT
Date: Fri, 23 Oct 2026 21:57:30 GMT
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Alt-Svc: h3=":443"; ma=93600
Content-Length: 2841

[{"RecallID":8298,"RecallNumber":"18136","RecallDate":"2018-04-04T00:00:00","Description":"This recall involves Vornado VH101 Personal Vortex electric space heaters sold in the following colors: black, coral orange, grayed jade, cinnamon, fig, ice white and red. The heaters measure about 7.2 inches long by 7.8 inches wide by 7.10 inches high and have two heat settings (low and high) and a fan only/no heat setting. \"Vornado\" with a \"V\" behind it is printed on the front of the unit. The model/type \"VH101,\" serial number and ETL mark are printed on a silver rating label on the bottom of the unit.","URL":"https://www.cpsc.gov/Recalls/2018/Vornado-Air-Recalls-Electric-Space-Heaters-Due-to-Fire-and-Burn-Hazards","Title":"Vornado Air Recalls Electric Space Heaters Due to Fire and Burn Hazards","ConsumerContact":"Vornado toll-free at 855-215-5131 from 8 a.m. to 5p.m. CT Monday through Friday or online at www.vornado.com and click on “Recalls” in the lower right corner of the homepage or www.vornado.com/recalls and click on the VH101 Personal Heater recall button for more information.","LastPublishDate":"2018-04-04T00:00:00","Products":[{"Name":"VH101 Personal Vortex electric space heaters","Description":"","Model":"","Type":"","CategoryID":"","NumberOfUnits":"About 350,000"}],"Inconjunctions":[],"Images":[{"URL":"https://www.cpsc.gov/s3fs-public/Picture1_36.png","Caption":""},{"URL":"https://www.cpsc.gov/s3fs-public/Picture2_29.png","Caption":""},{"URL":"https://www.cpsc.gov/s3fs-public/Picture3_18.png","Caption":""},{"URL":"https://www.cpsc.gov/s3fs-public/Picture4_11.png","Caption":""},{"URL":"https://www.cpsc.gov/s3fs-public/Picture5_7.png","Caption":""},{"URL":"https://www.cpsc.gov/s3fs-public/Picture6_4.png","Caption":""},{"URL":"https://www.cpsc.gov/s3fs-public/Picture7_3.png","Caption":""},{"URL":"https://www.cpsc.gov/s3fs-public/Picture8_1.png","Caption":""}],"Injuries":[{"Name":"Vornado has received 15 reports of the heaters catching on fire."}],"Manufacturers":[],"Retailers":[{"Name":"Bed Bath & Beyond, Home Depot, Menards, Orchard Supply, Target and other stores nationwide and online at Amazon.com, Target.com, Vornado.com and other websites from August 2009 through March 2018 for about $30.","CompanyID":""}],"Importers":[{"Name":"Vornado Air LLC, of Andover, Kan.","CompanyID":""}],"Distributors":[],"SoldAtLabel":null,"ManufacturerCountries":[{"Country":"China"}],"ProductUPCs":[],"Hazards":[{"Name":"The electric space heater can overheat when in use, posing fire and burn hazards.","HazardType":"","HazardTypeID":""}],"Remedies":[{"Name":"Consumers should immediately stop using the recalled heaters and contact Vornado for instructions on how to receive a full refund or a free replacement unit, including free shipping."}],"RemedyOptions":[{"Option":"Refund"},{"Option":"Replace"}]}]
```

## Instant Pot Smart WiFi 6 Qt (product)

### Fields that matter

| Field | Value as shown |
| --- | --- |
| recall_numbers | none |
| query.ProductName=Instant Pot Smart WiFi.record_count | 0 |

### Source evidence

### Product query

Exact query: GET https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant+Pot+Smart+WiFi
Retrieved (UTC): 2026-10-23T21:57:31Z

CPSC returned 0 record(s) for this query.
No records returned for this query; this is not a product safety clearance.

Source: <https://www.saferproducts.gov/RestWebServices/Recall?format=json&ProductName=Instant+Pot+Smart+WiFi>
```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Strict-Transport-Security: max-age=31536000 ; includeSubDomains ; preload
Pragma: no-cache
Server: Microsoft-IIS/10.0
X-AspNet-Version: 4.0.30319
X-Powered-By: ASP.NET
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: POST, GET, PUT, DELETE, OPTIONS
Cache-Control: no-cache
Expires: Fri, 23 Oct 2026 21:57:31 GMT
Date: Fri, 23 Oct 2026 21:57:31 GMT
Alt-Svc: h3=":443"; ma=93600
Content-Length: 2

[]
```
