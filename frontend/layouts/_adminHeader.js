import Head from "next/head"
import Image from "next/image"
import Link from "next/link"

import { useRouter } from "next/router"
import { useState, useEffect } from "react"

import { Nav } from "react-bootstrap"
import { Button } from "react-bootstrap"
import Dropdown from 'react-bootstrap/Dropdown'
import DropdownButton from 'react-bootstrap/DropdownButton'

import service from "../service"

import headerStyles from "../styles/AdminHeader.module.css"

export default function AdminHeader({ children }) {
  const router = useRouter()

  let { parserId } = router.query

  const [parser, setParser] = useState(null)

  const [user, setUser] = useState(null)

  const getParser = () => {
    if (!parserId) return
    service.get("parsers/" + parserId + "/", (response) => {
      setParser(response.data)
    })
  }

  const getUser = () => {
    service.get("user/", (response) => {
      setUser(response.data)
    })
  }

  const logoutBtnClickHandler = () => {
    service.post("rest-auth/logout/", {}, () => {
      localStorage.removeItem("token")
      router.push("/")
    })
  }

  useEffect(() => {
    getUser()
  }, [])

  useEffect(() => {
    getParser()
  }, [parserId])

  return (
    <header className={headerStyles.header}>
        <div>
            <div className="row" style={{ padding: 0, margin: 0 }}>
                <div
                className="col-6 col-md-6"
                style={{ paddingLeft: 20, paddingRight: 0 }}
                >
                <div className={headerStyles.logoDiv}>
                  <Link href={
                    router.pathname.split("/")[1] == "admin"
                      ? "/admin/parsers"
                      : "/workbench/parsers"
                  }>
                  <img
                  src="/static/img/logo.png"
                  width="40"
                  height="36"
                  alt="Cashew Docparser"
                  />
                </Link>
              </div>
                <Link href={
                  router.pathname.split("/")[1] == "admin"
                    ? "/admin/parsers"
                      : "/workbench/parsers"
                }>
                  <h2>Cashew</h2>
                </Link>
                &nbsp;&nbsp;&nbsp;
                <a
                    href="#"
                    onClick={() => router.back()}
                    style={{ display: "inline-block", verticalAlign: "top", marginRight: 10 }}
                  >
                  <i className={ headerStyles.parsersIcon + " bi bi-arrow-90deg-left" }></i>
                </a>
                <Nav.Link
                    href="/admin/parsers"
                    style={{ display: "inline-block", verticalAlign: "top" }}
                >
                    <i className={ headerStyles.parsersIcon + " bi bi-grid" }
                    ></i>
                </Nav.Link>
                </div>
                <div
                className="col-6 col-md-6"
                style={{ paddingLeft: 0, paddingRight: 20 }}
                >
                <nav className={headerStyles.nav}>
                    <ul>
                    <li>
                        <DropdownButton id="dropdown-basic-button" title="Account">
                        {user && (
                            <Dropdown.Item href="#">Welcome, {user.profile.fullName}</Dropdown.Item>
                        )}
                        <Dropdown.Item
                          href={
                            router.pathname.split("/")[1] == "admin"
                              ? "/workbench/parsers"
                              : "/admin/parsers"
                          }
                        >
                          {router.pathname.split("/")[1] == "admin"
                            ? "Switch to Workbench"
                            : "Switch to Workspace"}
                        </Dropdown.Item>
                        <Dropdown.Item href="/account/profile">Account Management</Dropdown.Item>
                        <Dropdown.Item href="#" onClick={logoutBtnClickHandler}>Logout</Dropdown.Item>
                        </DropdownButton>
                    </li>
                    </ul>
                </nav>
                </div>
            </div>
        </div>
    </header>
    );
}
