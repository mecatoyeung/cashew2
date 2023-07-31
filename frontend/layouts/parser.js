import Head from 'next/head'
import Image from "next/image"
import { useRouter } from 'next/router'

import { Button } from 'react-bootstrap'

import service from '../service'

import workspaceLayoutStyles from "../styles/WorkspaceLayout.module.css"

export default function ParserLayout({
    children
  }) {

  const router = useRouter()

  const logoutBtnClickHandler = () => {
    service.post("rest-auth/logout/", {}
      , () => {
        localStorage.removeItem("token")
      router.push("/")
    })
  }

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"></meta>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={workspaceLayoutStyles.wrapper}>
        <header className={workspaceLayoutStyles.header}>
          <div className="container-md">
            <div className="row">
              <div className="col-4 col-md-4">
                <div className={workspaceLayoutStyles.logoDiv}>
                  <Image src="/static/img/logo.png" width="40" height="36" alt="Cashew Docparser" />
                </div>
                <h1 className={workspaceLayoutStyles.h1}>Cashew</h1>
              </div>
              <div className="col-8 col-md-8">
                <nav className={workspaceLayoutStyles.nav}>
                  <ul>
                    <li>Welcome, Cato Yeung!</li>
                    <li>
                      <Button className="btn" onClick={logoutBtnClickHandler}>Logout</Button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>
          </div>
        </header>
        <hr className={workspaceLayoutStyles.headerHr}/>
        <main className={workspaceLayoutStyles.main + " d-flex flex-column"}>
          <div className={workspaceLayoutStyles.sideNavContainerDiv + " container-md d-flex flex-grow-1"}>
            <div className="row d-flex flex-grow-1">
              <div className="col-12" style={{paddingLeft: 0, paddingRight: 0}}>
                {children}
              </div>
            </div>
          </div>
        </main>
        <footer className={workspaceLayoutStyles.footer}>
          <div className="container">
            <div className="row">
              <div className="col-sm col-lg-8">
                <div className={workspaceLayoutStyles.copyright}>
                  2023 @ Sonik Global Limited. All rights reserved.
                </div>
              </div>
              <div className="col-sm col-lg-4">
                <div className="social-media">
                  <i className="fa fa-instagram" aria-hidden="true"></i>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}