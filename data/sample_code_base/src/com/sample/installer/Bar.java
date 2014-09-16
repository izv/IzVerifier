import com.izforge.izpack.installer.AutomatedInstallData;
import com.izforge.izpack.util.AbstractUIProcessHandler;
import com.izforge.izpack.util.VariableSubstitutor;

public Class Bar {

    public static void main(String [] args) {

    AutomatedInstallData installData = AutomatedInstallData.getInstance();
    Messages mess = idata.getMessages();

    String barString1 = mess.get("my.izpack5.key.3");
    String barString2 = mess.get("my.izpack5.key.4");
    }

}