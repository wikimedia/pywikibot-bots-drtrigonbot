<?xml version="1.0" encoding="iso-8859-1"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!-- generate HTML skeleton on root element -->
<xsl:template match="/rss">
<html>
<head>
    <!--<title><xsl:apply-templates select="channel/title"/></title>-->
    <title><xsl:value-of select="channel/title"/></title>
    <meta http-equiv="Content-Type" Content="text/html; charset=UTF-8" />
            
        <link type="text/css" rel="stylesheet" href="http://tools.wmflabs.org/drtrigonbot/batch.css" media="all" />
<link type="text/css" rel="stylesheet" href="http://tools.wmflabs.org/drtrigonbot/jira.webresources:global-static.css" media="all" />
<!--<script type="text/javascript" src="https://jira.toolserver.org/s/en_US-4gdbhi/733/10/1/_/download/superbatch/js/batch.js" ></script>-->
<!--<script type="text/javascript" src="https://jira.toolserver.org/s/en_US-4gdbhi/733/10/1/_/download/superbatch/js/batch.js?cache=false" ></script>-->

        <style type="text/css">

.tableBorder, .grid
{
    background-color: #fff;
    width: 100%;
    border-collapse: collapse;
}

.tableBorder td, .grid td
{
    vertical-align: top;
    padding: 2px;
    border: 1px solid #ccc;
}

.noPadding
{
    padding: 0 !important;
}

h3 .subText
{
    font-size: 60%;
    font-weight: normal;
}

.tabLabel
{
    font-weight: bold;
    border: 1px solid #ccc;
    border-bottom:none;
    padding: 2px;
    display: inline;
}

td.blank
{
    padding: 0;
    margin: 0;
}

.blank td
{
    border: none;
}

#descriptionArea
{
    margin: 0;
    padding: 2px;
    border: 1px solid #ccc;
}

hr
{
    border-top:1px solid #aaa;
}

hr.fullcontent
{
  height: 15px;
  padding: 10px 0;
  background: #fff url('https://jira.toolserver.org/images/icons/hr.gif') no-repeat scroll center;
}

</style>

</head>
<body>
        <xsl:apply-templates/>

Generated at Sun Jan 26 12:29:37 UTC 2014 using JIRA 5.0.6#733-sha1:f48fab7a0abaa0a316c14a3fc86cdf5a6805ba12.

</body>
</html>
</xsl:template>

<!-- convert items to HTML headings -->
<xsl:template match="item">
<table class="tableBorder" cellpadding="0" cellspacing="0" border="0" width="100%">
    <tr>
        <td bgcolor="#f0f0f0" width="100%" colspan="2" valign="top">
            <xsl:if test="parent != ''">
                <xsl:variable name="data" select="parent"/>
                            <b><a><xsl:attribute name="id">
                                   parent_issue_summary
                                  </xsl:attribute>
                                  <xsl:attribute name="href">
                                   https://jira.toolserver.org/browse/<xsl:value-of select="parent"/>
                                  </xsl:attribute>
                                  <xsl:value-of select="//item[key=$data]/summary"/><xsl:if test="not(//item[key=$data])">(n/a)</xsl:if></a></b>
                <span style="font-size: 9px">(<a><xsl:attribute name="id">
                                                  parent_issue_key
                                                 </xsl:attribute>
                                                 <xsl:attribute name="href">
                                                  https://jira.toolserver.org/browse/<xsl:value-of select="parent"/>
                                                 </xsl:attribute>
                                                 <xsl:value-of select="parent"/></a>)</span>
            </xsl:if>
                            <h3 class="formtitle">
                            <xsl:if test="parent != ''">
                            <img src="https://jira.toolserver.org/images/icons/link_out_bot.gif" width="16" height="16" />
                            </xsl:if>
                        [<a><xsl:attribute name="href">
                             #<xsl:value-of select="key"/>
                            </xsl:attribute>
                            <xsl:attribute name="name">
                             <xsl:value-of select="key"/>
                            </xsl:attribute>
                            <xsl:value-of select="key"/></a>]
                        <a><xsl:attribute name="href">
                         <xsl:value-of select="link"/>
                        </xsl:attribute>
                        <xsl:value-of select="summary"/></a>

            <span class="subText">
               Created: <xsl:value-of select="created"/>
               <xsl:if test="updated != ''">
               Updated: <xsl:value-of select="updated"/>
               </xsl:if> 
               <xsl:if test="due != ''">
               Due: <xsl:value-of select="due"/>
               </xsl:if> 
               <xsl:if test="resolved != ''">
               Resolved: <xsl:value-of select="resolved"/>
               </xsl:if> 
                            </span>
            </h3>
        </td>
    </tr>
    <tr>
        <td width="20%"><b>Status:</b></td>
        <td width="80%"><xsl:value-of select="status"/></td>
    </tr>
    <tr>
        <td width="20%"><b>Project:</b></td>
        <td width="80%"><a><xsl:attribute name="href">
                            https://jira.toolserver.org/secure/BrowseProject.jspa?id=<xsl:value-of select="project/@id" />
                           </xsl:attribute>
                           <xsl:value-of select="project"/></a></td>
    </tr>

        <tr>
            <td><b>Component/s:</b></td>
            <td><xsl:for-each select="component">
                 <xsl:value-of select="."/>,
                </xsl:for-each><xsl:if test="not(component)">None</xsl:if></td>
    </tr>
    

        <tr>
            <td><b>Affects Version/s:</b></td>
            <td><xsl:for-each select="version">
                 <xsl:value-of select="."/>,
                </xsl:for-each><xsl:if test="not(version)">None</xsl:if></td>
    </tr>
    

        <tr>
            <td><b>Fix Version/s:</b></td>
            <td><xsl:for-each select="fixVersion">
                 <xsl:value-of select="."/>,
                </xsl:for-each><xsl:if test="not(fixVersion)">None</xsl:if></td>
    </tr>
    
            <tr>
            <td><b>Security Level:</b></td>
            <td><xsl:value-of select="security"/></td>
       </tr>
    </table>

<br />
<table class="grid" cellpadding="0" cellspacing="0" border="0" width="100%">
    <tr>
        <td bgcolor="#f0f0f0" valign="top" width="20%">
            <b>Type:</b>
        </td>
        <td bgcolor="#ffffff" valign="top"  width="30%" >
            <xsl:value-of select="type"/>
        </td>

                    <td bgcolor="#f0f0f0">
                <b>Priority:</b>
            </td>
            <td bgcolor="#ffffff" valign="top" nowrap="nowrap">
                <xsl:value-of select="priority"/>
            </td>
            </tr>
    <tr>
                        <td bgcolor="#f0f0f0" valign="top" width="20%">
                <b>Reporter:</b>
            </td>
            <td bgcolor="#ffffff" valign="top"  width="30%" >
                <a><xsl:attribute name="href">
                    https://jira.toolserver.org/secure/ViewProfile.jspa?name=<xsl:value-of select="reporter"/>
                   </xsl:attribute>
                   <xsl:value-of select="reporter"/></a>
                            </td>
        
                    <td bgcolor="#f0f0f0" width="20%">
                <b>Assignee:</b>
            </td>
            <td bgcolor="#ffffff" valign="top" nowrap="nowrap"  width="30%" >
                <a><xsl:attribute name="href">
                    https://jira.toolserver.org/secure/ViewProfile.jspa?name=<xsl:value-of select="assignee"/>
                   </xsl:attribute>
                   <xsl:value-of select="assignee"/></a>
                            </td>
            </tr>
    	<tr>
		<td bgcolor="#f0f0f0" width="20%">
			<b>Resolution:</b>
		</td>
		<td bgcolor="#ffffff" valign="top" width="30%" nowrap="nowrap">
                <xsl:value-of select="resolution"/>
                    </td>
                    <td bgcolor="#f0f0f0" width="20%">
                <b>Votes (Watches):</b>
            </td>
            <td bgcolor="#ffffff" valign="top" width="30%" nowrap="nowrap">
                <xsl:value-of select="votes"/>
                (<xsl:value-of select="watches"/>)
            </td>
        
    </tr>
    
        <tr>
        <td bgcolor="#f0f0f0" width="20%">
            <b>Labels:</b>
        </td>
        <td id="labels-27325-value" class="value" bgcolor="#ffffff" valign="top" colspan="3" nowrap="nowrap">
            <xsl:for-each select="labels/label">
             <xsl:value-of select="."/>,
            </xsl:for-each><xsl:if test="not(labels/label)">None</xsl:if></td>
    </tr>
    
    	<tr>
                <td bgcolor="#f0f0f0" width="20%"><b>T Remaining Estimate:</b></td>
        <td bgcolor="#ffffff" valign="top" nowrap="nowrap">
                            <xsl:value-of select="aggregatetimeremainingestimate"/><xsl:if test="not(aggregatetimeremainingestimate)">Not Specified</xsl:if>
                    </td>
        		<td bgcolor="#f0f0f0" width="20%"><b>Remaining Estimate:</b></td>
        <td bgcolor="#ffffff" valign="top" nowrap="nowrap" width="80%" colspan="3">
                            <xsl:value-of select="timeestimate"/><xsl:if test="not(timeestimate)">Not Specified</xsl:if>
            		</td>
    </tr>
    <tr>
                <td bgcolor="#f0f0f0" width="20%"><b>T Time Spent:</b></td>
        <td bgcolor="#ffffff" valign="top" nowrap="nowrap">
                            <xsl:value-of select="aggregatetimespent"/><xsl:if test="not(aggregatetimespent)">Not Specified</xsl:if>
                    </td>
                <td bgcolor="#f0f0f0" width="20%"><b>Time Spent:</b></td>
		<td bgcolor="#ffffff" valign="top" nowrap="nowrap" width="80%" colspan="3">
                            <xsl:value-of select="timespent"/><xsl:if test="not(timespent)">Not Specified</xsl:if>
            		</td>
	</tr>
    <tr>
                <td bgcolor="#f0f0f0" width="20%"><b>T Original Estimate:</b></td>
        <td bgcolor="#ffffff" valign="top" nowrap="nowrap">
                            Not Specified
                    </td>
                <td bgcolor="#f0f0f0" width="20%"><b>Original Estimate:</b></td>
		<td bgcolor="#ffffff" valign="top" nowrap="nowrap" width="80%" colspan="3">
                            Not Specified
            		</td>
    </tr>
    
      <xsl:if test="environment != ''">
    	<tr>

		<td bgcolor="#f0f0f0" width="20%" valign="top">
			<b>Environment:</b>
		</td>
		<td bgcolor="#ffffff" valign="top" colspan="3">
                <xsl:value-of select="environment" disable-output-escaping="yes"/>
		</td>
	</tr>
      </xsl:if> 
    </table>



    <br />

    	<table class="grid" cellpadding="0" cellspacing="0" border="0" width="100%">

            <xsl:if test="attachments/attachment/@id != ''">
                <tr>
            <td bgcolor="#f0f0f0" width="20%" valign="top">
                <b>Attachments:</b>
            </td>
            <td bgcolor="#ffffff" valign="top">
                <xsl:for-each select="attachments/attachment">
                    <img src="https://jira.toolserver.org/images/icons/attach/file.gif" height="16" width="16" alt="File" />
                    <xsl:value-of select="./@name"/> &#160;&#160;&#160;&#160;
                </xsl:for-each>
                </td>
            </tr>
            </xsl:if>


            <xsl:if test="issuelinks != ''">
            <tr>
            <td bgcolor="#f0f0f0" width="20%" valign="top">
                <b>Issue Links:</b>
            </td>
            <td bgcolor="#ffffff" valign="top" class="noPadding">
                <table cellpadding="0" cellspacing="0" border="0" width="100%" class="blank">
                    <xsl:for-each select="issuelinks/issuelinktype">
                                            <tr>
                            <td colspan="4" bgcolor="#f0f0f0">
                                <b><xsl:value-of select="name"/></b><br/>
                            </td>
                        </tr>
                    <xsl:for-each select="*/issuelink">
                                                                <tr>
            <td>
                <xsl:value-of select="../@description"/>
            </td>
            <xsl:variable name="data" select="issuekey"/>
            <td>
                <a><xsl:attribute name="href">
                    https://jira.toolserver.org/browse/<xsl:value-of select="issuekey"/>
                   </xsl:attribute>
                   <xsl:choose>
                     <xsl:when test="//item[key=$data]/status = 'Closed' or //item[key=$data]/status = 'Resolved'">
                       <strike><xsl:value-of select="issuekey"/></strike>
                     </xsl:when>
                     <xsl:otherwise>
                       <xsl:value-of select="issuekey"/>
                     </xsl:otherwise>
                   </xsl:choose></a>
            </td>
            <td>
                <xsl:value-of select="//item[key=$data]/summary"/><xsl:if test="not(//item[key=$data])">(n/a)</xsl:if>
            </td>
            <td>
                <xsl:value-of select="//item[key=$data]/status"/><xsl:if test="not(//item[key=$data])">(n/a)</xsl:if>
            </td>
        </tr>
                    </xsl:for-each>
                    </xsl:for-each>
                </table>
            </td>
        </tr>
            </xsl:if> 


            <xsl:if test="subtasks/subtask != ''">
<tr><td bgcolor="#f0f0f0" width="20%" valign="top"><b>Sub-Tasks:</b></td>
    <td bgcolor="#ffffff" valign="top">
        <table class="grid" cellpadding="0" cellspacing="0" border="0" width="100%">
            <tr bgcolor="#f0f0f0">
                <td>
                    <b>Key</b><br/>
                </td>
                <td>
                    <b>Summary</b><br/>
                </td>
                <td>
                    <b>Type</b><br/>
                </td>
                <td>
                    <b>Status</b><br/>
                </td>
                <td>
                    <b>Assignee</b><br/>
                </td>
            </tr>
            <xsl:for-each select="subtasks/subtask">
                            <tr>
                    <td>
                        <a><xsl:attribute name="href">
                            https://jira.toolserver.org/browse/<xsl:value-of select="."/>
                           </xsl:attribute>
                           <xsl:value-of select="."/></a>
                    </td>
                    <xsl:variable name="data" select="."/>
                    <td valign="top" width="25%">
                        <xsl:value-of select="substring(//item[key=$data]/summary,0,38)"/><xsl:if test="string-length(//item[key=$data]/summary)>38">...</xsl:if><xsl:if test="not(//item[key=$data])">(n/a)</xsl:if>
                    </td>
                    <td>
                        Sub-task
                    </td>
                    <td>
                        <xsl:value-of select="//item[key=$data]/status"/><xsl:if test="not(//item[key=$data])">(n/a)</xsl:if>
                    </td>
                    <td>
                        <xsl:value-of select="//item[key=$data]/assignee"/><xsl:if test="not(//item[key=$data])">(n/a)</xsl:if>
                    </td>
                </tr>
            </xsl:for-each>
                    </table>
    </td>
</tr>
            </xsl:if>


            <xsl:for-each select="customfields/customfield">
                        <tr>
                <td bgcolor="#f0f0f0" width="20%" valign="top"><b><xsl:value-of select="customfieldname"/>:</b></td>
                <td id="customfield_10010-27325-value" class="value" bgcolor="#ffffff" width="80%">
                <xsl:for-each select="customfieldvalues">
                    <xsl:choose>
                      <xsl:when test="../customfieldname = 'URL'">
                        <a><xsl:attribute name="href">
                            <xsl:value-of select="customfieldvalue"/>
                           </xsl:attribute>
                           <xsl:value-of select="customfieldvalue"/></a><br />
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="customfieldvalue"/><br />
                      </xsl:otherwise>
                    </xsl:choose>
                </xsl:for-each>
                </td>
            </tr>
            </xsl:for-each>

            </table>

    <br/>

    <xsl:if test="description != ''">
    <table cellpadding="2" cellspacing="0" border="0" width="100%" align="center">
    <tr>
        <td bgcolor="#bbbbbb" width="1%" nowrap="nowrap" align="center">
             <font color="#ffffff"><b>Description</b></font> 
        </td>
        <td> </td>
    </tr>
    </table>

    <table cellpadding="0" cellspacing="0" border="0" width="100%">
    <tr>
        <td id="descriptionArea">
            <xsl:value-of select="description" disable-output-escaping="yes"/>
        </td>
    </tr>
    </table>

    <br/>
    </xsl:if> 

    <table cellpadding="2" cellspacing="0" border="0" width="100%" align="center">
    <tr>
        <td bgcolor="#bbbbbb" width="1%" nowrap="nowrap" align="center">
             <font color="#ffffff"><b>Comments</b></font> 
        </td>
        <td> </td>
    </tr>
    </table>

    <table cellpadding="0" cellspacing="0" border="0" width="100%" class="grid" style="margin: 0;">

            <xsl:for-each select="comments/comment">
                <tr><xsl:attribute name="id">
                     comment-header-<xsl:value-of select="./@id"/>
                    </xsl:attribute>
                    <td bgcolor="#f0f0f0">
            Comment by <a><xsl:attribute name="class">
                           user-hover
                          </xsl:attribute>
                          <xsl:attribute name="rel">
                           <xsl:value-of select="./@author"/>
                          </xsl:attribute>
                          <xsl:attribute name="id">
                           word_commented_<xsl:value-of select="./@author"/>
                          </xsl:attribute>
                          <xsl:attribute name="href">
                           https://jira.toolserver.org/secure/ViewProfile.jspa?name=<xsl:value-of select="./@author"/>
                          </xsl:attribute>
                          <xsl:value-of select="./@author"/></a>
                                        <font size="-2">
            [
                <font color="#336699"><xsl:value-of select="./@created"/></font>

                            ]
            </font>

        </td></tr>
        <tr><xsl:attribute name="id">
             comment-body-<xsl:value-of select="./@id"/>
            </xsl:attribute><td bgcolor="#ffffff">
            <xsl:value-of select="." disable-output-escaping="yes"/>
        </td></tr>
            </xsl:for-each>

            </table>
<hr class='fullcontent' /><br /><br style='page-break-before:always;'/><br />

  <xsl:apply-templates/>
</xsl:template>

<!--<xsl:template match="item/description">-->
<!--  <p><xsl:apply-templates/></p>-->
<!--</xsl:template>-->

<xsl:template match="channel/title">
  <h2><xsl:apply-templates/></h2>
</xsl:template>

<xsl:template match="channel/link">
  <small><xsl:apply-templates/></small>
</xsl:template>

<xsl:template match="channel/description">
  <p><xsl:apply-templates/></p>
</xsl:template>

<xsl:template match="channel/description">
  <p><xsl:apply-templates/></p>
</xsl:template>

<!-- ignore, since handeled seperately -->
<xsl:template match="item/title">
</xsl:template>

<xsl:template match="item/link">
</xsl:template>

<xsl:template match="item/project">
</xsl:template>

<xsl:template match="item/key">
</xsl:template>

<xsl:template match="item/summary">
</xsl:template>

<xsl:template match="item/status">
</xsl:template>

<xsl:template match="item/created">
</xsl:template>

<xsl:template match="item/updated">
</xsl:template>

<xsl:template match="item/resolved">
</xsl:template>

<xsl:template match="item/due">
</xsl:template>

<xsl:template match="item/component">
</xsl:template>

<xsl:template match="item/version">
</xsl:template>

<xsl:template match="item/fixVersion">
</xsl:template>

<xsl:template match="item/security">
</xsl:template>

<xsl:template match="item/type">
</xsl:template>

<xsl:template match="item/priority">
</xsl:template>

<xsl:template match="item/reporter">
</xsl:template>

<xsl:template match="item/assignee">
</xsl:template>

<xsl:template match="item/resolution">
</xsl:template>

<xsl:template match="item/votes">
</xsl:template>

<xsl:template match="item/labels">
</xsl:template>

<xsl:template match="item/environment">
</xsl:template>

<xsl:template match="item/issuelinks">
</xsl:template>

<xsl:template match="item/attachements">
</xsl:template>

<xsl:template match="item/subtasks">
</xsl:template>

<xsl:template match="item/customfields">
</xsl:template>

<xsl:template match="item/description">
</xsl:template>

<xsl:template match="item/comments">
</xsl:template>

<xsl:template match="item/watches">
</xsl:template>

<xsl:template match="item/parent">
</xsl:template>

<xsl:template match="item/aggregatetimeremainingestimate">
</xsl:template>

<xsl:template match="item/timeestimate">
</xsl:template>

<xsl:template match="item/aggregatetimespent">
</xsl:template>

<xsl:template match="item/timespent">
</xsl:template>

</xsl:stylesheet>     
