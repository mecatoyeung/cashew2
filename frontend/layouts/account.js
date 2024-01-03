import Head from "next/head"
import Image from "next/image"
import Link from "next/link"

import { useRouter } from "next/router"
import { useState, useEffect } from "react"

import { Nav } from "react-bootstrap"
import { Button } from "react-bootstrap"
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownButton from 'react-bootstrap/DropdownButton'

import WorkspaceHeader from "./_workspaceHeader"

import service from "../service"

import accountStyles from "../styles/Account.module.css"

export default function AccountLayout({ children }) {
  const router = useRouter();

  let { } = router.query;

  useEffect(() => {
  }, [])

  return (
    <>
      <Head>
        <title>Cashew Docparser</title>
        <meta name="description" content="Written by Cato Yeung" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"
        ></meta>
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={accountStyles.wrapper}>
        <WorkspaceHeader/>
        <hr className={accountStyles.headerHr} />
        <main className={accountStyles.main + " d-flex flex-column"}>
          <div
            className={
              accountStyles.sideNavContainerDiv + " d-flex flex-grow-1"
            }
          >
            <div
              className="row d-flex flex-grow-1"
              style={{ padding: 0, margin: 0, flexDirection: "row" }}
            >
              <div
                className="col-12 col-md-2 d-flex"
                style={{ paddingLeft: 0, paddingRight: 0, width: 200 }}
              >
                <div
                  className={
                    accountStyles.sideNavDiv + " d-flex flex-grow-1"
                  }
                >
                  <ul className={accountStyles.sideNavUl}>
                    <li style={{ fontFamily: "Oswald, sans", fontSize: "130%" }}>Account</li>
                    <Link href={"/account/profile"}>
                      <li>Profile</li>
                    </Link>
                    <Link href={"/account/change-password"}>
                      <li>Change Password</li>
                    </Link>
                  </ul>
                </div>
              </div>
              <div
                className="col-12 col-md-10 flex-grow-1"
                style={{
                  paddingLeft: 0,
                  paddingRight: 0,
                  paddingBottom: 10,
                  minHeight: "480px",
                  display: "flex",
                  flexDirection: "column",
                  width: "calc(100% - 200px)",
                }}
              >
                {children}
              </div>
            </div>
          </div>
        </main>
        <footer className={accountStyles.footer}>
          <div style={{ width: "100%", padding: "0 10px" }}>
            <div className="row" style={{ padding: "0 10px" }}>
              <div className="col-sm" style={{ padding: "10px" }}>
                <div className={accountStyles.copyright}>
                  2023. All rights reserved.
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
