<?xml version="1.0"?>
<!-- http://www2.cs.uni-paderborn.de/cs/ag-engels/ag_dt/Courses/Lehrveranstaltungen/WS0607/WE/Assignments/FilesHW5/rss2html.xslt -->
<!-- http://www.koders.com/xml/fidB16620D75BF6B7B210D8D0E1A3E8611625A45D2C.aspx?s=httpwebrequest -->
<!-- Using XSaLT http://toolserver.org/~drtrigon/cgi-bin/xsalt.py?xslt=rss2html.xslt this is an alternative to
     feed2html (http://scott.yang.id.au/2005/05/feed2html/) with Universal Feed Parser (http://feedparser.org/) -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output 
     method="html"
     doctype-public="-//W3C//DTD HTML 4.01 Transitional//EN"
     encoding="UTF-8"
     indent="yes"
     />

   <xsl:template match="/">
      <html>
         <head>
<!--Title-->
            <title>
               <xsl:value-of select="rss/channel/title"/>
               <xsl:text> - RSS </xsl:text>
               <xsl:value-of select="rss/@version" />
            </title>
         </head>
         <body>
<!--Headline-->
         <h1>
            <xsl:value-of select="rss/channel/title" />
            <xsl:text> - </xsl:text>
<!--            <xsl:value-of select="rss/channel/pubDate" />-->
            <xsl:value-of select="rss/channel/lastBuildDate" />
         </h1>
<!--Link-->
                <h2>
           <xsl:element name="a">
               <xsl:attribute name="href">
               <xsl:value-of select="rss/channel/link"/>
              </xsl:attribute>
              <xsl:value-of select="rss/channel/link"/>
           </xsl:element>
           <xsl:text> - </xsl:text>
           <xsl:value-of select="rss/channel/description" />
          </h2>      
<!--Table-->
            <table border="1">
               <xsl:apply-templates select="rss/channel/item">
<!--                  <xsl:sort select="pubDate" order="descending"/>-->
               </xsl:apply-templates>
            </table>
         </body>
      </html>
   </xsl:template>

   <xsl:template match="item">
      <tr>
         <td rowspan="2">
            <xsl:value-of select="pubDate" />
         </td>
         <td>
          <b>
             <xsl:value-of disable-output-escaping="yes" select="title" />
            </b>
         </td>
      </tr>
      <tr>
         <td>
            <xsl:value-of disable-output-escaping="yes" select="description" />
               <xsl:element name="a">
                <xsl:attribute name="href">
                   <xsl:value-of select="link"/>
                </xsl:attribute>
                <xsl:text>weiter...</xsl:text>
             </xsl:element>
         </td>
      </tr>
   </xsl:template>

</xsl:stylesheet>
