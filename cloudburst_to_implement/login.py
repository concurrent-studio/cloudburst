self.session = self.get_anonymous_session()
self.login_username = ""

def get_anonymous_session(self) -> requests.Session:
        """Returns our default anonymous requests.Session object."""
        session = requests.Session()
        session.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                                'ig_vw': '1920', 'csrftoken': '',
                                's_network': '', 'ds_user_id': ''})
        session.headers.update(self._default_http_header(empty_session_only=True))
        if self.request_timeout is not None:
            # Override default timeout behavior.
            # Need to silence mypy bug for this. See: https://github.com/python/mypy/issues/2427
            session.request = partial(session.request, timeout=self.request_timeout) # type: ignore
        return session

def session_graphql_query(self, query_hash: str, variables: Dict[str, Any]:
        """
        Do a GraphQL Query.
        :param query_hash: Query identifying hash.
        :param variables: Variables for the Query.
        :param referer: HTTP Referer, or None.
        :param rhx_gis: 'rhx_gis' variable as somewhere returned by Instagram, needed to 'sign' request
        :return: The server's response dictionary.
        """
        with copy_session(self._session) as tmpsession:
            tmpsession.headers.update(self._default_http_header(empty_session_only=True))
            del tmpsession.headers['Connection']
            del tmpsession.headers['Content-Length']
            tmpsession.headers['authority'] = 'www.instagram.com'
            tmpsession.headers['scheme'] = 'https'
            tmpsession.headers['accept'] = '*/*'
            if referer is not None:
                tmpsession.headers['referer'] = urllib.parse.quote(referer)

            variables_json = json.dumps(variables, separators=(',', ':'))

            if rhx_gis:
                #self.log("rhx_gis {} query_hash {}".format(rhx_gis, query_hash))
                values = "{}:{}".format(rhx_gis, variables_json)
                x_instagram_gis = hashlib.md5(values.encode()).hexdigest()
                tmpsession.headers['x-instagram-gis'] = x_instagram_gis

            resp_json = self.get_json('graphql/query',
                                      params={'query_hash': query_hash,
                                              'variables': variables_json},
                                      session=tmpsession)
        if 'status' not in resp_json:
            self.error("GraphQL response did not contain a \"status\" field.")
        return resp_json

def _default_http_header(self, empty_session_only: bool = False) -> Dict[str, str]:
        """Returns default HTTP header we use for requests."""
        header = {'Accept-Encoding': 'gzip, deflate',
                  'Accept-Language': 'en-US,en;q=0.8',
                  'Connection': 'keep-alive',
                  'Content-Length': '0',
                  'Host': 'www.instagram.com',
                  'Origin': 'https://www.instagram.com',
                  'Referer': 'https://www.instagram.com/',
                  'User-Agent': self.user_agent,
                  'X-Instagram-AJAX': '1',
                  'X-Requested-With': 'XMLHttpRequest'}
        if empty_session_only:
            del header['Host']
            del header['Origin']
            del header['Referer']
            del header['X-Instagram-AJAX']
            del header['X-Requested-With']
        return header

def do_sleep(self):
        """Sleep a short time if self.sleep is set. Called before each request to instagram.com."""
        if self.sleep:
            time.sleep(min(random.expovariate(0.7), 5.0))

def login(username, password):
    http.client._MAXHEADERS = 200
    session = requests.Session()
    session.cookies.update({'sessionid': '', 'mid': '', 'ig_pr': '1',
                            'ig_vw': '1920', 'ig_cb': '1', 'csrftoken': '',
                            's_network': '', 'ds_user_id': ''})
    session.headers.update(self._default_http_header())
    
    # if self.request_timeout is not None:
    #     # Override default timeout behavior.
    #     # Need to silence mypy bug for this. See: https://github.com/python/mypy/issues/2427
    #     session.request = partial(session.request, timeout=self.request_timeout) # type: ignore
    session.get('https://www.instagram.com/web/__mid/')
    csrf_token = session.cookies.get_dict()['csrftoken']
    session.headers.update({'X-CSRFToken': csrf_token})
    # Not using self.get_json() here, because we need to access csrftoken cookie
    self.do_sleep()
    login = session.post('https://www.instagram.com/accounts/login/ajax/',
                            data={'password': passwd, 'username': user}, allow_redirects=True)
    try:
        resp_json = login.json()
    except json.decoder.JSONDecodeError:
        raise ConnectionException("Login error: JSON decode fail, {} - {}.".format(login.status_code, login.reason))
    if resp_json.get('two_factor_required'):
        # two_factor_session = copy_session(session, self.request_timeout)
        # two_factor_session.headers.update({'X-CSRFToken': csrf_token})
        # two_factor_session.cookies.update({'csrftoken': csrf_token})
        # self.two_factor_auth_pending = (two_factor_session,
        #                                 user,
        #                                 resp_json['two_factor_info']['two_factor_identifier'])
        # raise TwoFactorAuthRequiredException("Login error: two-factor authentication required.")
        print("TWO FACTOR FUCK")
    if resp_json.get('checkpoint_url'):
        raise ConnectionException("Login: Checkpoint required. Point your browser to "
                                    "https://www.instagram.com{} - "
                                    "follow the instructions, then retry.".format(resp_json.get('checkpoint_url')))
    if resp_json['status'] != 'ok':
        if 'message' in resp_json:
            raise ConnectionException("Login error: \"{}\" status, message \"{}\".".format(resp_json['status'],
                                                                                            resp_json['message']))
        else:
            raise ConnectionException("Login error: \"{}\" status.".format(resp_json['status']))
    if 'authenticated' not in resp_json:
        # Issue #472
        if 'message' in resp_json:
            raise ConnectionException("Login error: Unexpected response, \"{}\".".format(resp_json['message']))
        else:
            raise ConnectionException("Login error: Unexpected response, this might indicate a blocked IP.")
    if not resp_json['authenticated']:
        if resp_json['user']:
            # '{"authenticated": false, "user": true, "status": "ok"}'
            raise BadCredentialsException('Login error: Wrong password.')
        else:
            # '{"authenticated": false, "user": false, "status": "ok"}'
            # Raise InvalidArgumentException rather than BadCredentialException, because BadCredentialException
            # triggers re-asking of password in Instaloader.interactive_login(), which makes no sense if the
            # username is invalid.
            raise InvalidArgumentException('Login error: User {} does not exist.'.format(user))
    # '{"authenticated": true, "user": true, "userId": ..., "oneTapPrompt": false, "status": "ok"}'
    session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
    self.session = session
    self.login_username = username