require 'socket'      

class KServer
  attr_accessor :s
  
  def initialize(host)
    @s = TCPSocket::new(host, 9020) 
    @name = "unknown"
    @chatbuffer = []
  end

  def color(c, m)
    27.chr + "[0;40;" + c + "m" + m + 27.chr + "[0m"
  end

  def yellow(m)
    color("33", m)
  end

  def blue(m)
    color("34", m)
  end

  def red(m)
    color("31", m)
  end

  def getline()
    m = s.gets("\r\n").chomp
    puts yellow(m)
    m
  end

  def send_receive(msg)
    puts blue(msg)
    s.write(msg + "\r\n")
    getline()
  end

  def send_receive_no_print(msg)
    puts blue(msg)
    s.write(msg + "\r\n")
    s.gets("\r\n").chomp
  end

  def send_raw(msg)
    puts blue(msg)
    s.write(msg)
  end

  def send_with_rn(msg)
    puts blue(msg)
    s.write(msg + "\r\n")
  end

  def send_expect_socket_close(msg)
    puts blue(msg)
    s.write(msg + "\r\n")

    begin
      m = s.recv(1)
    rescue
      puts red("FAIL:\n#m\ndoesn't match\n#{ "Expected EOF/CLOSE SOCKET"}")
    end
  end

  def send_expect(m, e)
    res = send_receive_no_print(m).chomp
    if ( res == e )
      puts yellow(res)
    else
      puts red("FAIL:\n#{res}\ndoesn't match\n#{e}")
    end
  end



  def randomchar()
    a= "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    a[rand(a.length)].chr
  end

  def randomword()
    (1 + rand(10)).times.collect { randomchar() }.join
  end

  def randomspace()
    (1 + rand(5)).times.collect { " " }.join()
  end

  def randomwords()
    (1 + rand(10)).times.collect { randomword() }.join(randomspace())
  end

  def random()
    case rand(6)
    when 0
      send_receive("help")
    when 1
      rw = randomwords()
      send_expect( "test: " + rw, rw)
    when 2
      @name = randomword()
      send_expect( "name: " + @name, "OK")
    when 3
      rw = randomwords()
      @chatbuffer.push("#{@name}: #{rw}")
      send_expect( "push: " + rw, "OK")
    when 4
      send_expect( "get", @chatbuffer.join("\n"))
    when 5
      en = if @chatbuffer.size == 0 then 0 else rand( @chatbuffer.size ) end
      st = if en == 0 then 0 else rand( en ) end
      send_expect("getrange #{st} #{en}", @chatbuffer[st..en].join("\n"))
    end
  end

end

if ARGV.length == 0
  puts "USAGE"
  puts "ruby prj1_test.rb IP_OR_HOSTNAME normal"
  puts "ruby prj1_test.rb IP_OR_HOSTNAME evil"
  puts "ruby prj1_test.rb IP_OR_HOSTNAME random"
  exit
end

s = KServer.new(ARGV[0])
if ARGV[1] == "random"
  s.getline
  for x in 1..25 do
    s.random()
  end
  s.send_expect_socket_close("adios")
elsif ARGV[1] == "evil"
  s.getline
  s.send_with_rn("help\r\nhelp")
  s.getline
  #s.getline

  s.send_raw("hel")
  sleep(5)
  s.send_with_rn("p")
  s.getline
  s.getline

  s.send_raw("bogus\n")
  s.send_raw("bogus\n")
  s.send_raw("bogus\n")
  s.send_receive("bogus")
  s.send_expect_socket_close("adios")
else #normal
  s.getline
  s.send_receive("name: bozo")
  s.send_receive("name: bozo")                                                                                           
  s.send_receive("help")                                                                                                 
  s.send_receive("test: foo bar loo")                                                                                    
  s.send_receive("name: bozo")                                                                                           
  s.send_receive("push: hello mom")                                                                                      
  s.send_receive("get")                                                                                                  
  s.send_receive("push: hello dad")                                                                                      
  s.send_receive("push: hello sister")                                                                                   
  s.send_receive("push: hello brother")                                                                                  
  s.send_receive("getrange 1 3")                                                                                         
  s.send_expect_socket_close("adios")
end