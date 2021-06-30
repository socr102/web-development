<?php
   function get_encoded_header(){
       $API_KEY = "nqzum2aq44amvq8g8b8wbqx4";
       $SECRET_KEY = "2FgCD9uN8b";
       $authorization_string = $API_KEY.":".$SECRET_KEY;
       $authorization_header_encoded = base64_encode($authorization_string);
       return  $authorization_header_encoded;
   }

   function get_access_token($authorization_header_encoded){
        $TOKEN_ENDPOINT = 'https://api.manheim.com/oauth2/token.oauth2';
        $data = array('grant_type' => 'client_credentials');
        $options = array(
            'http' => array(
                'header'  => "Authorization: Basic ".$authorization_header_encoded."\r\n", "Content-type: application/x-www-form-urlencoded",
                'method'  => 'POST',
                'content' => http_build_query($data)
            )
        );
        $context  = stream_context_create($options);

        $result = file_get_contents($TOKEN_ENDPOINT, false, $context);
        if ($result === FALSE) { /* Handle error */ }
        return json_decode($result,true);
   }
   
   function has_token_expires($token){
        $opts = array(
            'http'=>array(
            'method'=>"GET",
            'header'=>"Authorization: ".$token['token_type']." ".$token['access_token']
            )
        );
        
        $context = stream_context_create($opts);
        
        // Open the file using the HTTP headers set above
        $file = file_get_contents('https://api.manheim.com/oauth2/token/status', false, $context);

        #$status = json_decode($file,true);
        $status_line = $http_response_header[0];
        preg_match('{HTTP\/\S*\s(\d{3})}', $status_line, $match);
        $status = $match[1];
        
        if ($status == 200)
            return False;
        else
            return True;
   }

   function get_data($token = NULL){
        
        if($token ==NULL || has_token_expires($token)!=True)
            {
                $header = get_encoded_header();
                $token = get_access_token($header);
            }

        $opts = array(
            'http'=>array(
            'method'=>"GET",
            'header'=>"Authorization: ".$token['token_type']." ".$token['access_token']
            )
        );
        
        $context = stream_context_create($opts);
        // Open the file using the HTTP headers set above
        $file = file_get_contents('https://api.manheim.com/valuations/vin/1VWAH7A34DC146014?include=retail,historical,forecast', false, $context);

        return json_decode($file,true);
   }
   $get_data = get_data(NULL);
   var_dump($get_data);
?>