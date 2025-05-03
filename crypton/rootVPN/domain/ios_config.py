from jinja2 import Template
import uuid
from django.http import HttpResponse

def generate_ios_config(username: str, password: str, server_url: str):
    """Генерирует конфиг для iOS (IKEv2 + EAP) без SharedSecret и сертификатов"""
    config_template = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>IKEv2</key>
            <dict>
                <key>AuthenticationMethod</key>
                <string>None</string>
                <key>RemoteAddress</key>
                <string>{{ server_url }}</string>
                <key>RemoteIdentifier</key>
                <string>{{ server_url }}</string>
                <key>LocalIdentifier</key>
                <string>{{ username }}</string>
                <key>ExtendedAuthEnabled</key>
                <true/>
                <key>AuthName</key>
                <string>{{ username }}</string>
                <key>AuthPassword</key>
                <string>{{ password }}</string>
                <!-- Убрано упоминание сертификата -->
            </dict>
            <key>PayloadDescription</key>
            <string>VPN (IKEv2)</string>
            <key>PayloadDisplayName</key>
            <string>VPN {{ username }}</string>
            <key>PayloadIdentifier</key>
            <string>com.example.vpn.ikev2.{{ payload_uuid }}</string>
            <key>PayloadType</key>
            <string>com.apple.vpn.managed</string>
            <key>PayloadUUID</key>
            <string>{{ payload_uuid }}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
            <key>UserDefinedName</key>
            <string>VPN (IKEv2)</string>
            <key>VPNType</key>
            <string>IKEv2</string>
            <!-- Добавлены важные параметры для работы без сертификатов -->
            <key>IKESecurityAssociationParameters</key>
            <dict>
                <key>EncryptionAlgorithm</key>
                <string>AES-256</string>
                <key>IntegrityAlgorithm</key>
                <string>SHA2-256</string>
                <key>DiffieHellmanGroup</key>
                <integer>14</integer>
            </dict>
        </dict>
    </array>
    <key>PayloadDescription</key>
    <string>Настройки VPN (IKEv2)</string>
    <key>PayloadDisplayName</key>
    <string>VPN {{ username }}</string>
    <key>PayloadIdentifier</key>
    <string>com.example.profile.{{ profile_uuid }}</string>
    <key>PayloadOrganization</key>
    <string>Your Company</string>
    <key>PayloadRemovalDisallowed</key>
    <false/>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{{ profile_uuid }}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
    """
    
    template = Template(config_template)
    return template.render(
        username=username,
        password=password,
        server_url=server_url,
        payload_uuid=str(uuid.uuid4()),
        profile_uuid=str(uuid.uuid4())
    )

def download_vpn_profile(request):
    username = request.GET.get("username", "default_user")
    password = request.GET.get("password", "default_password")
    url = request.GET.get("url", "vpn.example.com")

    config_content = generate_ios_config(username, password, url)
    
    response = HttpResponse(
        config_content,
        content_type="application/x-apple-aspen-config"
    )
    response["Content-Disposition"] = f'attachment; filename=vpn_{username}_{uuid.uuid4().hex[:12]}.mobileconfig"'
    return response