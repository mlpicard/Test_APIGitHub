#!C:/Perl64/bin/perl.exe
$|=1;       # buffer flush (allows instant printing)
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use CGI ':standard';
use strict;
use LWP::UserAgent;
use JSON;

print header(-'content-encoding'=>'no',-charset=>'UTF-8'); warningsToBrowser(1);
my $submit=(param('submit')) ? param('submit') : '';
my $search=(param('search'))? param('search'): '';
my $repoFullName=(param('repo'))? param('repo') : '';
if (param('ACT') eq 'getRepositoryInfo'){&getRepositoryInfo; exit;}

##> hash to associate a color to a language
my %languageColor=(
                   'Go' => '#FC0F0F',
                   'PHP' => '#5660B7',
                   'JavaScript' => '#62F776',
                   'Python' => '#FF84F8',
                   'Java' => '#4F0D4A',
                   'Ruby' => '#38AEC9',
                   'Hack' => '#F97C0E',
                   'Shell' => '#35133D',
                   'Elixir' => '#1823F7',
                   'Roff' => '#F9F348',
                   'HTML' => '#DD82C5',
                   'C' => '#1A6D38', 
                   'Swift' => '#76F2EE',
                   'C++' => '#961616',
                   'Haskell' => '#171147',
                   'Clojure' => '#F4D85D'
                   );

##>starting HTML
print qq
|<HTML>
    <HEAD>
        <TITLE>GitHub repository informations</TITLE>
        <LINK rel="stylesheet" href="/style.css" type="text/css">
        <LINK href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">
        <SCRIPT src="https://code.jquery.com/jquery-3.3.1.min.js" type='text/javascript'></SCRIPT>
        <SCRIPT src="http://cdn.jsdelivr.net/jquery.flot/0.8.3/jquery.flot.min.js"></SCRIPT>
        <SCRIPT src="http://cdn.jsdelivr.net/jquery.flot/0.8.3/jquery.flot.time.js"></SCRIPT>
        <SCRIPT LANGUAGE="JavaScript">
            // AJAX --->
            function getXMLHTTP() {
                var xhr=null;
                if(window.XMLHttpRequest) {// Firefox & others
                    xhr = new XMLHttpRequest();
                }
                else if(window.ActiveXObject){ // Internet Explorer
                    try {
                      xhr = new ActiveXObject("Msxml2.XMLHTTP");
                    } catch (e) {
                        try {
                            xhr = new ActiveXObject("Microsoft.XMLHTTP");
                        } catch (e1) {
                            xhr = null;
                        }
                    }
                }
                else { // XMLHttpRequest not supported by browser
                    alert("Your browser does not support XMLHTTPRequest objects...");
                }
                return xhr;
            }
            
            
            /*use ajax to get informations about the selected repository*/
            function ajaxGetRepositoriesInfo (repoFullName,repoID){
                var url="test.cgi?ACT=getRepositoryInfo&repo="+repoFullName;
                \$.ajax({
                    url: url,
                    type: 'GET'
                })
                .done (function(resultat){
                    \$('#DIVrepositoryInfo').html(resultat);
                    \$('#DIVrepositoriesList').hide();
                    \$('#DIVselectedRepo').html(\$('#DIVrepo'+repoID).html());
                    
                })
                .fail (function(XHR,statut,error){
                    \$('#DIVrepositoryInfo').html(error);
                });
            }
            //<--- AJAX
        </SCRIPT>
    </HEAD>
    <BODY>
        <CENTER>
            <HEADER class="mainDIV">
                <FONT class="title1">Analysis of the GitHub repositories</FONT><BR><BR><BR>
                Use this page to search for a GitHub repository<BR>
                based on its name.
            </HEADER>
            <DIV class="formDIV" id="formDIV">
                <FORM method="GET" action="./test.cgi" name="parameters" enctype="multipart/form-data">
                    Enter a GitHub repository name <BR><BR>
                    <INPUT class="search" id="searchItem" name="searchItem" type="text" required><BR>
                    <INPUT class="input" type="reset" name="clear" value="Clear">
                    <INPUT class="input" type="submit" name="submit" value="Search">
                </FORM>
            </DIV>
        </CENTER>
|;

##> process the results form
if ($submit){
    
    ##> make the request to search repositories
    my $searchItem=param('searchItem');
    my $agent = LWP::UserAgent->new();
    $agent->proxy('http','http://www-cache.curie.fr:3128/');
    my $URL="https://api.github.com/search/repositories?q=$searchItem";
    my @headers=('Accept'=>"application/vnd.github.mercy-preview+json");
    my $response = $agent->get($URL);
    
    ###> recovering repositories informations
    my %repositoriesInfo;
    if ($response->is_success) {
        my $res=decode_json($response->content);
        my $maxCount=$res->{'total_count'} - 1;
        for my $i (0..$maxCount){
            my $repoName=$res->{'items'}[$i]->{'name'};
            my $repoDes=$res->{'items'}[$i]->{'description'};
            my $repoStargazers=$res->{'items'}[$i]->{'stargazers_count'};
            my $repoLanguage=$res->{'items'}[$i]->{'language'};
            my $repoFullName=$res->{'items'}[$i]->{'full_name'};
            my $repoForks=$res->{'items'}[$i]->{'forks_count'};
            my $repoUpdateDate=$res->{'items'}[$i]->{'updated_at'};
            my $score=$res->{'items'}[$i]->{'score'};
            my $id=$res->{'items'}[$i]->{'id'};
            my $link='https://github.com/'.$repoFullName;
            $repositoriesInfo{$id}=[$score,$repoName,$repoDes,$repoStargazers,$repoLanguage,$repoFullName,$repoForks,$link,$repoUpdateDate];
        }
    }
    else{
        print "Error", $response->status_line;
    }
    
    ###> modifie the position of the search form
    print qq|
        <SCRIPT>
            var formDiv=document.getElementById(\"formDIV\");
            formDiv.style.position='fixed';
            formDiv.style.left='10%';
        </SCRIPT>
    |;
    
    ###> display repositories list and informations
    print "<BR><BR><BR><DIV id=\"DIVrepositoriesList\">";
    if (scalar keys %repositoriesInfo !=0){
        foreach my $repositoryID (sort {$repositoriesInfo{$b}[0] <=> $repositoriesInfo{$a}[0]} keys %repositoriesInfo){
            next unless $repositoriesInfo{$repositoryID}[5];
            my $addClass='';
            ##> repository name
            print qq |
                <DIV class="resultDIV"  id="DIVrepo$repositoryID">
                    <B><FONT class="title2"><A id="repo:$repositoryID" class="alink" href="javascript:ajaxGetRepositoriesInfo('$repositoriesInfo{$repositoryID}[5]',$repositoryID);">$repositoriesInfo{$repositoryID}[5]</A></FONT></B><BR><BR>
            |;
            
            ##> comments
            print "$repositoriesInfo{$repositoryID}[2]<BR>" if $repositoriesInfo{$repositoryID}[2];
            
            ##> stargazer number
            unless ($repositoriesInfo{$repositoryID}[3]==0){
                print qq |
                    <svg aria-label="star" viewBox="0 0 14 16" version="1.1" width="14" height="16" role="img" class="star"><path fill-rule="evenodd" d="M14 6l-4.9-.64L7 1 4.9 5.36 0 6l3.6 3.26L2.67 14 7 11.67 11.33 14l-.93-4.74L14 6z"></path></svg>
                    $repositoriesInfo{$repositoryID}[3]
                |;
                $addClass='class="marge"';
            }
            
            ##> fork number
            if ($repositoriesInfo{$repositoryID}[6]){
                print qq |
                    <SPAN $addClass>
                        <SPAN class="language" style="background-color:#000000;"></SPAN>
                        $repositoriesInfo{$repositoryID}[6]
                    </SPAN>
                |;
            }
            
            ##> language
            if ($repositoriesInfo{$repositoryID}[4]){
                print qq |
                    <SPAN $addClass>
                        <SPAN class="language" style="background-color:$languageColor{$repositoriesInfo{$repositoryID}[4]};"></SPAN>
                        $repositoriesInfo{$repositoryID}[4]<BR>
                    </SPAN>
                |;
            }
            else{
                print "<BR>";
            }
            
            ##> updated date
            if ($repositoriesInfo{$repositoryID}[8]){
                my $date=&convertDate($repositoriesInfo{$repositoryID}[8]);
                print "Updated on ".$date."<BR>";
            }
            print "</DIV><BR><HR><BR>";
        }
    }
    else{
        print "<DIV class=\"resultDIV\">No repositories found.</DIV>";
    }
    print qq |
        </DIV>
        <DIV class="resultDIV" id="DIVselectedRepo"></DIV>
        <DIV class="resultDIV" id="DIVrepositoryInfo"></DIV>
    </BODY>
</HTML>
    |;
}

sub convertDate{
    ##> used to convert a date string to 'Day Month Year'
    my $param=$_[0];
    $param=~s/T.+//;
    my @dateSplit=split(/-/,$param);
    my %month=(
                '01'=>'Jan',
                '02'=>'Feb',
                '03'=>'Mar',
                '04'=>'Apr',
                '05'=>'May',
                '06'=>'Jun',
                '07'=>'Jul',
                '08'=>'Aug',
                '09'=>'Sep',
                '10'=>'Oct',
                '11'=>'Nov',
                '12'=>'Dec',
                );
    my $date=$dateSplit[2].' '.$month{$dateSplit[1]}.' '.$dateSplit[0]; # day month year
    return $date;
}

sub getRepositoryInfo {
    ###> recovering committers and commits informations
    my (%commitsInfo,%commitsNumber,%commitsTimeLine);
    my $agent = LWP::UserAgent->new(); 
    my $URL="https://api.github.com/repos/$repoFullName/commits?per_page=100";
    my @headers=('Accept'=>'application/vnd.github.cloak-preview','User-Agent'=>'mlpicard');
    my $response = $agent->get($URL,@headers);
    if ($response->is_success) {
        my $res=decode_json($response->content);
        for my $i (0..scalar @{$res}-1){
            my $committer=$res->[$i]{'author'}{'login'};
            my $committerURL=$res->[$i]{'author'}{'html_url'};
            my $avatarURL=$res->[$i]{'author'}{'avatar_url'};
            my $lastDate=$res->[$i]{'commit'}{'committer'}{'date'};
            my $commitMessage=$res->[$i]{'commit'}{'message'};
            $commitsNumber{$committer}++;       ##> store the number of commits per committer
            my $date=&convertDate($lastDate);    
            $commitsTimeLine{$date}++;      ##> store the number of commits per date
            $commitsInfo{$committer}=[$committerURL,$avatarURL,$lastDate] unless $commitsInfo{$committer}; ###> store committer informations (avatar, url)
        }
    }
    else{
        print "Error", $response->status_line;
    }
    
    ###> display informations about committers and commits number
    print "<FONT class=\"title2\">Committers list </FONT>";
    print "<TABLE cellspacing=5 >";
    foreach my $committer (sort {$commitsNumber{$b} <=> $commitsNumber{$a}} keys %commitsInfo){
        next unless $committer;
        my ($url,$avatarURL,$dateGlobal)=@{$commitsInfo{$committer}};
        my $date=&convertDate($dateGlobal); 
        print qq |
            <TR >
                <TD align="left">
        |;
        print "<IMG src=\"$avatarURL\"/>" if $avatarURL;
        print qq |
                </TD>
                <TD align="left" class="committer"><A href="$url">$committer</A></TD>
            </TR>
            <TR>
                <TD align="left">&nbsp;</TD>
                <TD align="left">Commits number on the last hundred : $commitsNumber{$committer}</TD>
            </TR>
            
            <TR>
                <TD align="left">&nbsp;</TD>
                <TD align="left" style="padding-top:10px;padding-bottom:30px;">Last commit date : $date</TD>
            </TR>
        |;
    }
    print "</TABLE>";
    
    
    ###> use the plot function of jquery to display the commits timeline
    print qq |
    <BR><BR><FONT class="title2">Last 100 commits timeline </FONT><BR><BR>
    <DIV id="placeholder" style="width:1000px;height:400px;margin-left:-150px;"></DIV>
    <SCRIPT LANGUAGE="JavaScript">
        var rawData=[];
        var label=[];
        |;
        my $indx=0;
        foreach my $date (sort keys %commitsTimeLine) {
            print "rawData[$indx]=[$indx,$commitsTimeLine{$date}];\n";      ##> date and number of commits per date
            print "label[$indx]=[$indx,'$date'];\n";        ##> used to set the date in xaxis
            $indx++;
        }
        print qq |
        var options = {
         series: {
                lines: { show: true }
            },
            xaxis: {
                ticks: label
            }
        }
        \$(document).ready(function () {
            \$.plot(\$("#placeholder"),[
                {                    
                   data: rawData
                }
            ], 
            options);
        });
    </SCRIPT>
    |;
    
}