import jenkins.model.*
import hudson.security.*

import hudson.security.csrf.DefaultCrumbIssuer
import jenkins.model.Jenkins
import jenkins.security.s2m.*

import jenkins.*;
import hudson.model.*;



def instance = Jenkins.getInstance()

println "--> creating local user 'admin'"

def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount('admin','admin')
instance.setSecurityRealm(hudsonRealm)

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
instance.setAuthorizationStrategy(strategy)
instance.save()

// Change it to the DNS name if you have it
jlc = JenkinsLocationConfiguration.get()
jlc.setUrl("http://127.0.0.1:8080")
jlc.save()

Jenkins.instance.injector.getInstance(AdminWhitelistRule.class)
    .setMasterKillSwitch(false);
Jenkins.instance.save()

if(!Jenkins.instance.isQuietingDown()) {
    def j = Jenkins.instance
    if(j.getCrumbIssuer() == null) {
        j.setCrumbIssuer(new DefaultCrumbIssuer(true))
        j.save()
        println 'CSRF Protection configuration has changed.  Enabled CSRF Protection.'
    }
    else {
        println 'Nothing changed.  CSRF Protection already configured.'
    }
}
else {
    println "Shutdown mode enabled.  Configure CSRF protection SKIPPED."
}

def rule = Jenkins.instance.getExtensionList(jenkins.security.s2m.MasterKillSwitchConfiguration.class)[0].rule
if(!rule.getMasterKillSwitch()) {
    rule.setMasterKillSwitch(true)
    //dismiss the warning because we don't care (cobertura reporting is broken otherwise)
    Jenkins.instance.getExtensionList(jenkins.security.s2m.MasterKillSwitchWarning.class)[0].disable(true)
    Jenkins.instance.save()
    println 'Disabled agent -> master security for cobertura.'
}
else {
    println 'Nothing changed.  Agent -> master security already disabled.'
}



// disabled CLI access over TCP listener (separate port)
def p = AgentProtocol.all()
p.each { x ->
  if (x.name.contains("CLI")) p.remove(x)
}

// disable CLI access over /cli URL
def removal = { lst ->
  lst.each { x -> if (x.getClass().name.contains("CLIAction")) lst.remove(x) }
}
def j = Jenkins.instance;
removal(j.getExtensionList(RootAction.class))
removal(j.actions)

println "--> Disable Jenkins CLI Remoting interface"
Jenkins.instance.getDescriptor("jenkins.CLI").get().setEnabled(false)